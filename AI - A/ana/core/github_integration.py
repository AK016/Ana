#!/usr/bin/env python3
# Ana AI Assistant - GitHub Integration Module

import os
import re
import json
import time
import logging
import subprocess
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger('Ana.GitHubIntegration')

class GitHubIntegration:
    """GitHub integration for Ana AI Assistant's self-evolution capabilities"""
    
    def __init__(self, settings):
        """Initialize GitHub integration with settings"""
        self.settings = settings
        self.enabled = settings.get("github", {}).get("enabled", False)
        
        # GitHub settings
        github_settings = settings.get("github", {})
        self.username = github_settings.get("username", "")
        self.email = github_settings.get("email", "")
        self.token = github_settings.get("token", "")
        self.repo_url = github_settings.get("repo_url", "")
        self.main_branch = github_settings.get("main_branch", "main")
        self.auto_push = github_settings.get("auto_push", False)
        
        # Local repo settings
        self.repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Git command history
        self.command_history = []
        self.last_sync_time = time.time()
        self.sync_interval = 3600  # 1 hour
        
        # Thread for auto-sync
        self.running = False
        self.sync_thread = None
        
        logger.info("GitHub integration initialized")
    
    def start(self):
        """Start GitHub integration services"""
        if not self.enabled:
            logger.info("GitHub integration is disabled in settings")
            return False
            
        # Verify git is installed
        if not self._check_git_installed():
            logger.error("Git is not installed or not in PATH")
            return False
        
        # Configure git credentials if needed
        self._configure_git()
        
        # Check repository status
        status = self._check_repo_status()
        if not status["initialized"]:
            logger.warning("Git repository not initialized")
            if self._init_repository():
                logger.info("Git repository initialized successfully")
            else:
                logger.error("Failed to initialize Git repository")
                return False
        
        # Start auto-sync thread if enabled
        if self.auto_push:
            self.running = True
            self.sync_thread = threading.Thread(target=self._auto_sync_loop, daemon=True)
            self.sync_thread.start()
            logger.info("GitHub auto-sync started")
        
        logger.info("GitHub integration started successfully")
        return True
    
    def _check_git_installed(self) -> bool:
        """Check if git is installed and accessible"""
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True, text=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _configure_git(self):
        """Configure git credentials"""
        if self.username and self.email:
            try:
                # Set user name and email
                subprocess.run(["git", "config", "user.name", self.username], cwd=self.repo_dir, check=True)
                subprocess.run(["git", "config", "user.email", self.email], cwd=self.repo_dir, check=True)
                
                # Configure credential helper if token is provided
                if self.token:
                    subprocess.run(["git", "config", "credential.helper", "store"], cwd=self.repo_dir, check=True)
                    
                    # Store credentials in a secure way (this is a simplified approach)
                    repo_domain = self._extract_domain_from_url(self.repo_url)
                    if repo_domain:
                        # Create a temporary credential file
                        cred_file = os.path.expanduser("~/.git-credentials-temp")
                        with open(cred_file, "w") as f:
                            f.write(f"https://{self.username}:{self.token}@{repo_domain}\n")
                        
                        # Import credentials
                        subprocess.run(["git", "credential", "approve"], input=f"url=https://{repo_domain}\nusername={self.username}\npassword={self.token}\n", text=True, cwd=self.repo_dir)
                        
                        # Remove temporary file
                        os.remove(cred_file)
                
                logger.info("Git credentials configured")
            except subprocess.SubprocessError as e:
                logger.error(f"Error configuring git: {str(e)}")
    
    def _extract_domain_from_url(self, url: str) -> Optional[str]:
        """Extract domain from repository URL"""
        if not url:
            return None
            
        # Match pattern like https://github.com/username/repo.git or git@github.com:username/repo.git
        https_match = re.match(r"https://([^/]+)/", url)
        ssh_match = re.match(r"git@([^:]+):", url)
        
        if https_match:
            return https_match.group(1)
        elif ssh_match:
            return ssh_match.group(1)
        else:
            return None
    
    def _check_repo_status(self) -> Dict[str, Any]:
        """Check status of the git repository"""
        status = {
            "initialized": False,
            "current_branch": None,
            "uncommitted_changes": False,
            "remote_configured": False
        }
        
        try:
            # Check if .git directory exists
            git_dir = os.path.join(self.repo_dir, ".git")
            if not os.path.isdir(git_dir):
                return status
            
            status["initialized"] = True
            
            # Get current branch
            result = subprocess.run(["git", "branch", "--show-current"], 
                                   cwd=self.repo_dir, capture_output=True, text=True, check=True)
            status["current_branch"] = result.stdout.strip()
            
            # Check for uncommitted changes
            result = subprocess.run(["git", "status", "--porcelain"], 
                                   cwd=self.repo_dir, capture_output=True, text=True, check=True)
            status["uncommitted_changes"] = bool(result.stdout.strip())
            
            # Check if remote is configured
            result = subprocess.run(["git", "remote", "-v"], 
                                   cwd=self.repo_dir, capture_output=True, text=True, check=True)
            status["remote_configured"] = bool(result.stdout.strip())
            
            return status
            
        except subprocess.SubprocessError as e:
            logger.error(f"Error checking repository status: {str(e)}")
            return status
    
    def _init_repository(self) -> bool:
        """Initialize git repository"""
        try:
            # Initialize repository if not already initialized
            if not os.path.isdir(os.path.join(self.repo_dir, ".git")):
                subprocess.run(["git", "init"], cwd=self.repo_dir, check=True)
                logger.info("Git repository initialized")
            
            # Add remote if URL is provided and remote is not configured
            if self.repo_url:
                remote_result = subprocess.run(["git", "remote", "-v"], 
                                             cwd=self.repo_dir, capture_output=True, text=True)
                
                if "origin" not in remote_result.stdout:
                    subprocess.run(["git", "remote", "add", "origin", self.repo_url], 
                                  cwd=self.repo_dir, check=True)
                    logger.info(f"Added remote: origin -> {self.repo_url}")
            
            # Create initial commit if repo is empty
            status_result = subprocess.run(["git", "status"], 
                                         cwd=self.repo_dir, capture_output=True, text=True)
            
            if "No commits yet" in status_result.stdout:
                # Create README.md if it doesn't exist
                readme_path = os.path.join(self.repo_dir, "README.md")
                if not os.path.exists(readme_path):
                    with open(readme_path, "w") as f:
                        f.write("# Ana AI Assistant\n\n")
                        f.write("This repository contains the Ana AI Assistant codebase.\n")
                        f.write(f"Initial commit created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Commit
                subprocess.run(["git", "add", "."], cwd=self.repo_dir, check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit by Ana AI"], 
                              cwd=self.repo_dir, check=True)
                logger.info("Created initial commit")
            
            return True
            
        except subprocess.SubprocessError as e:
            logger.error(f"Error initializing repository: {str(e)}")
            return False
    
    def _auto_sync_loop(self):
        """Background loop for automatic synchronization"""
        while self.running:
            try:
                # Check if it's time to sync
                if time.time() - self.last_sync_time > self.sync_interval:
                    # Check for changes
                    status = self._check_repo_status()
                    if status["uncommitted_changes"]:
                        # Auto-commit changes
                        self.commit_changes(f"Auto-commit: System updates on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                    
                    # Pull and push changes
                    self.sync_with_remote()
                    self.last_sync_time = time.time()
                
                # Sleep to avoid high CPU usage
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in auto-sync loop: {str(e)}")
                time.sleep(1800)  # Sleep longer after an error (30 minutes)
    
    def commit_changes(self, message: str, files: List[str] = None) -> bool:
        """Commit changes to the repository"""
        if not self.enabled:
            logger.warning("GitHub integration is disabled")
            return False
            
        try:
            # Check for changes
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         cwd=self.repo_dir, capture_output=True, text=True)
            
            if not status_result.stdout.strip():
                logger.info("No changes to commit")
                return True  # Not an error, just nothing to do
            
            # Add files
            if files:
                # Add specific files
                for file in files:
                    file_path = os.path.join(self.repo_dir, file)
                    if os.path.exists(file_path):
                        subprocess.run(["git", "add", file], cwd=self.repo_dir, check=True)
            else:
                # Add all changes
                subprocess.run(["git", "add", "."], cwd=self.repo_dir, check=True)
            
            # Commit changes
            result = subprocess.run(["git", "commit", "-m", message], 
                                   cwd=self.repo_dir, capture_output=True, text=True)
            
            # Check if commit was successful
            if "nothing to commit" in result.stdout or "nothing added to commit" in result.stdout:
                logger.info("No changes to commit")
                return True
            elif result.returncode == 0:
                logger.info(f"Changes committed: {message}")
                self.command_history.append(f"Commit: {message}")
                return True
            else:
                logger.error(f"Commit failed: {result.stderr}")
                return False
                
        except subprocess.SubprocessError as e:
            logger.error(f"Error committing changes: {str(e)}")
            return False
    
    def create_branch(self, branch_name: str, from_branch: str = None) -> bool:
        """Create a new branch"""
        if not self.enabled:
            logger.warning("GitHub integration is disabled")
            return False
            
        try:
            # Get current branch if from_branch not specified
            if not from_branch:
                result = subprocess.run(["git", "branch", "--show-current"], 
                                      cwd=self.repo_dir, capture_output=True, text=True, check=True)
                from_branch = result.stdout.strip() or self.main_branch
            
            # Create branch
            subprocess.run(["git", "checkout", "-b", branch_name, from_branch], 
                          cwd=self.repo_dir, check=True)
            
            logger.info(f"Created and switched to branch '{branch_name}' from '{from_branch}'")
            self.command_history.append(f"Create branch: {branch_name} from {from_branch}")
            return True
            
        except subprocess.SubprocessError as e:
            logger.error(f"Error creating branch: {str(e)}")
            return False
    
    def switch_branch(self, branch_name: str) -> bool:
        """Switch to a different branch"""
        if not self.enabled:
            logger.warning("GitHub integration is disabled")
            return False
            
        try:
            # Check if branch exists
            result = subprocess.run(["git", "branch"], 
                                  cwd=self.repo_dir, capture_output=True, text=True, check=True)
            
            branches = [b.strip() for b in result.stdout.replace("*", "").split("\n") if b.strip()]
            
            # Create branch if it doesn't exist
            if branch_name not in branches:
                logger.warning(f"Branch '{branch_name}' doesn't exist, creating it")
                return self.create_branch(branch_name)
            
            # Switch to branch
            subprocess.run(["git", "checkout", branch_name], 
                          cwd=self.repo_dir, check=True)
            
            logger.info(f"Switched to branch '{branch_name}'")
            self.command_history.append(f"Switch to branch: {branch_name}")
            return True
            
        except subprocess.SubprocessError as e:
            logger.error(f"Error switching branch: {str(e)}")
            return False
    
    def pull_changes(self, branch: str = None) -> bool:
        """Pull changes from remote repository"""
        if not self.enabled:
            logger.warning("GitHub integration is disabled")
            return False
            
        try:
            # Determine branch to pull
            if not branch:
                result = subprocess.run(["git", "branch", "--show-current"], 
                                      cwd=self.repo_dir, capture_output=True, text=True, check=True)
                branch = result.stdout.strip() or self.main_branch
            
            # Pull changes
            result = subprocess.run(["git", "pull", "origin", branch], 
                                  cwd=self.repo_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully pulled changes from '{branch}'")
                self.command_history.append(f"Pull from: origin/{branch}")
                return True
            else:
                # Check for specific error patterns
                if "conflict" in result.stderr.lower():
                    logger.error(f"Pull failed due to conflicts: {result.stderr}")
                    return False
                elif "not found" in result.stderr.lower():
                    logger.warning(f"Remote branch '{branch}' not found. Creating new branch.")
                    return True  # Not a failure, just a new branch
                else:
                    logger.error(f"Pull failed: {result.stderr}")
                    return False
                
        except subprocess.SubprocessError as e:
            logger.error(f"Error pulling changes: {str(e)}")
            return False
    
    def push_changes(self, branch: str = None, force: bool = False) -> bool:
        """Push changes to remote repository"""
        if not self.enabled:
            logger.warning("GitHub integration is disabled")
            return False
            
        try:
            # Determine branch to push
            if not branch:
                result = subprocess.run(["git", "branch", "--show-current"], 
                                      cwd=self.repo_dir, capture_output=True, text=True, check=True)
                branch = result.stdout.strip() or self.main_branch
            
            # Push changes
            cmd = ["git", "push", "origin", branch]
            if force:
                cmd.append("--force")
                
            result = subprocess.run(cmd, cwd=self.repo_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully pushed changes to 'origin/{branch}'")
                self.command_history.append(f"Push to: origin/{branch}")
                return True
            else:
                logger.error(f"Push failed: {result.stderr}")
                return False
                
        except subprocess.SubprocessError as e:
            logger.error(f"Error pushing changes: {str(e)}")
            return False
    
    def sync_with_remote(self) -> bool:
        """Synchronize with remote repository (pull and push)"""
        if not self.enabled:
            logger.warning("GitHub integration is disabled")
            return False
            
        # Pull changes first
        pull_success = self.pull_changes()
        
        # Push local changes
        push_success = self.push_changes()
        
        return pull_success and push_success
    
    def create_feature_branch(self, feature_name: str) -> str:
        """Create a new branch for feature development"""
        # Sanitize branch name
        branch_name = f"feature/{re.sub(r'[^\w-]', '_', feature_name.lower())}"
        
        # Create branch
        if self.create_branch(branch_name, self.main_branch):
            return branch_name
        else:
            return None
    
    def commit_feature(self, feature_name: str, files: List[str], commit_message: str = None) -> bool:
        """Commit changes for a specific feature"""
        if not commit_message:
            commit_message = f"Add feature: {feature_name}"
            
        # Create branch if needed
        status = self._check_repo_status()
        if status["current_branch"] != f"feature/{feature_name}":
            branch_name = f"feature/{re.sub(r'[^\w-]', '_', feature_name.lower())}"
            
            # Check if branch exists
            result = subprocess.run(["git", "branch"], 
                                  cwd=self.repo_dir, capture_output=True, text=True)
            
            if branch_name in result.stdout:
                self.switch_branch(branch_name)
            else:
                self.create_feature_branch(feature_name)
        
        # Commit changes
        return self.commit_changes(commit_message, files)
    
    def create_pull_request(self, title: str, description: str, source_branch: str, target_branch: str = None) -> Dict[str, Any]:
        """Create a pull request on GitHub"""
        if not self.enabled or not self.token:
            logger.warning("GitHub integration or token is not available")
            return {"success": False, "message": "GitHub integration or token not available"}
            
        # Default target branch
        if not target_branch:
            target_branch = self.main_branch
            
        try:
            # Extract owner and repo from URL
            owner_repo_match = re.search(r'github\.com[/:]([\w-]+)/([\w-]+)', self.repo_url)
            if not owner_repo_match:
                return {"success": False, "message": "Could not parse GitHub repository URL"}
                
            owner, repo = owner_repo_match.groups()
            repo = repo.replace(".git", "")
            
            # Create PR using GitHub API
            import requests
            
            # Ensure all changes are pushed
            self.push_changes(source_branch)
            
            # Create PR
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            data = {
                "title": title,
                "body": description,
                "head": source_branch,
                "base": target_branch
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code in (200, 201):
                pr_data = response.json()
                logger.info(f"Created pull request #{pr_data['number']}: {title}")
                
                return {
                    "success": True,
                    "pr_number": pr_data["number"],
                    "url": pr_data["html_url"]
                }
            else:
                error_msg = response.json().get("message", "Unknown error")
                logger.error(f"Failed to create PR: {error_msg}")
                
                return {"success": False, "message": error_msg}
                
        except Exception as e:
            logger.error(f"Error creating pull request: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def get_command_history(self) -> List[str]:
        """Get history of git commands executed"""
        return self.command_history
    
    def shutdown(self):
        """Shutdown GitHub integration"""
        logger.info("Shutting down GitHub integration")
        self.running = False
        
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=2.0)
        
        # Commit any pending changes before shutdown
        if self.enabled and self.auto_push:
            status = self._check_repo_status()
            if status["uncommitted_changes"]:
                self.commit_changes(f"Auto-commit on shutdown: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                self.push_changes() 