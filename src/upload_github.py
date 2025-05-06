import git
import os
import shutil
import textwrap

def upload_files_to_github(token, repo_url, directory_path, commit_message):
    """
    Upload the contents of a directory to a GitHub repository.

    Parameters:
    - token (str): GitHub or GitLab personal access token.
    - repo_url (str): HTTPS URL of the repository.
    - directory_path (str): Path to the local directory whose contents need to be uploaded.
    - commit_message (str): Commit message.

    Returns:
    - None: Prints success or error messages.
    """
    try:
        # Create a temporary directory for the repository clone
        repo_dir = '/tmp/repo_clone'
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)  # Remove if it already exists

        # Modify the repo URL to include the token
        if "github.com" in repo_url:
            authenticated_repo_url = repo_url.replace("https://", f"https://{token}@")
        else:
            authenticated_repo_url = repo_url.replace("https://", f"https://oauth2:{token}@")

        # Clone the repository
        repo = git.Repo.clone_from(authenticated_repo_url, repo_dir, depth=1)
        
        # Copy all contents from the given directory to the cloned repository directory
        for item in os.listdir(directory_path):
            src_path = os.path.join(directory_path, item)
            dest_path = os.path.join(repo_dir, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)
        
        with open(f'{repo_dir}/.gitignore', 'w') as git_ignore:
            content = textwrap.dedent("""\
                                    .DS_Store
                                    *tmp*
                                    cache/*
                                    filtered*
                                    raw*
""")
            git_ignore.write(content)

        # Stage all changes, commit, and push
        repo.git.add(A=True)  # Add all changes
        repo.index.commit(commit_message)
        repo.remote(name='origin').push()

        # Clean up the temporary directory
        shutil.rmtree(repo_dir)

        print(f'Success! The contents of {directory_path} have been uploaded to the repository.')

    except Exception as e:
        print(f'Failed to upload directory: {e}')
