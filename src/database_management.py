import sqlite3
import json
import logging
from src.misc_functions import similar

logger = logging.getLogger(__name__)

def create_database(db_name="channels_streams.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the channels table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            picon TEXT
        )
    ''')

    # Create the streams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            link TEXT NOT NULL,
            availability TEXT,
            last_seen TEXT,
            resolution TEXT,
            codec TEXT,
            channel_id INTEGER NOT NULL,
            FOREIGN KEY (channel_id) REFERENCES channels (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def add_channels(db_name, channels):
    """
    Add a list of channels to the database.
    Prevent adding channels if any name already exists.
    :param db_name: Name of the SQLite database file
    :param channels: List of tuples (names, picon), where `names` can be a single string or a list of strings.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Fetch all existing channel names from the database
    cursor.execute('SELECT name FROM channels')
    existing_names = []
    for row in cursor.fetchall():
        try:
            existing_names.extend(json.loads(row[0]))  # Deserialize JSON stored in the 'name' column
        except json.JSONDecodeError:
            existing_names.append(row[0])  # Add as-is if not JSON

    for channel in channels:
        # Ensure the channel is a tuple of (names, picon)
        if len(channel) != 2:
            raise ValueError("Each channel must be a tuple of (names, picon).")

        names, picon = channel

        # Convert names to a JSON array for storage
        if isinstance(names, list):
            names_json = json.dumps(names)
        elif isinstance(names, str):
            names_json = json.dumps([names])  # Convert single string to a JSON array
        else:
            raise ValueError("Channel names must be a string or a list of strings.")

        # Check for duplicate names
        if any(name in existing_names for name in json.loads(names_json)):
            logger.debug(f"Channel not added: A channel with names {names} already exists in the database.")
            continue

        # Add the channel if no conflicts were found
        cursor.execute('''
            INSERT INTO channels (name, picon) VALUES (?, ?)
        ''', (names_json, picon))
        logger.info(f"Channel added: {names}")

    conn.commit()
    conn.close()


def add_stream(db_name, stream):
    """
    Add or update a single stream in the database.
    If the stream.link already exists, update the existing entry.
    :param db_name: Name of the SQLite database file
    :param stream: Tuple (name, link, availability, last_seen, resolution, codec, channel_id)
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if the stream link already exists
    cursor.execute('SELECT id FROM streams WHERE link = ?', (stream.link,))
    existing_stream = cursor.fetchone()
    status_stream = 'Active' if stream.availability else 'Offline'
    if existing_stream:
        # Update the existing stream
        cursor.execute('''
            UPDATE streams
            SET name = ?, availability = ?, last_seen = ?, resolution = ?, codec = ?, channel_id = ?
            WHERE link = ?
        ''', (stream.name, stream.availability, stream.last_seen, stream.resolution, stream.video_codec, stream.channel_id, stream.link))
        print(f"Stream updated: {stream.link} - {stream.name} - {status_stream}.")
    else:
        # Add a new stream
        cursor.execute('''
            INSERT INTO streams (name, link, availability, last_seen, resolution, codec, channel_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (stream.name, stream.link, stream.availability, stream.last_seen, stream.resolution, stream.video_codec, stream.channel_id))
        print(f"Stream added: {stream.link} - {stream.name} - {status_stream}.")

    conn.commit()
    conn.close()

def find_channel_id(database_path, stream_name):
    """
    Find if a stream name corresponds to a channel name in the database and return the channel_id.

    Args:
        database_path (str): Path to the SQLite database file.
        stream_name (str): Name of the stream to search for.

    Returns:
        int: The channel_id if a match is found, None otherwise.
    """
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Fetch all channels
        query = "SELECT id, name FROM channels"
        cursor.execute(query)
        channels = cursor.fetchall()

        conn.close()
        # Search for the stream_name in the deserialized channel names
        for channel_id, channel_names in channels:
            try:
                name_list = json.loads(channel_names)
                if similar(name_list, stream_name, threshold=0.96):
                    return channel_id
            except json.JSONDecodeError:
                pass  # Ignore rows with invalid JSON
        return 0
    except sqlite3.Error as e:
        logger.error(f'Database error: {e}')
        return 0

def fetch_stream_details(db_name, channel_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        query = """
        SELECT s.link, s.codec, s.resolution
        FROM streams s
        JOIN channels c ON s.channel_id = c.id
        WHERE c.name = ? and s.availability = '1'
        """
        cursor.execute(query, (f"{channel_name}",))
        results = cursor.fetchall()

        conn.close()
        return results
    except sqlite3.Error as e:
        logger.error(f'Database error: {e}')
        return []

def fetch_logo(db_name, channel_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        query = """
        SELECT picon 
        FROM channels
        WHERE name = ?;
        """
        cursor.execute(query, (f"{channel_name}",))
        results = cursor.fetchone()
        conn.close()
        if results:
            tv_logo = results[0]
            return tv_logo
        return results
    except sqlite3.Error as e:
        logger.error(f'Database error: {e}')
        return 'https://gitlab.blackbirdrecordings.com/cvzero89/livetv/-/raw/main/icon/404.png'