# Gitea Deployment Script

This repository contains a Python script to automate the deployment of a cloud infrastructure for Gitea, including:

- A MySQL database running on a separate virtual machine.
- A Gitea instance running on another virtual machine.
- All communication occurs within a private network.
- Persistent repository data is stored on an external disk, which can be relocated.

## Prerequisites

- Hetzner Cloud API token.
- SSH public key available locally.
- Python 3.x installed with required libraries.

## Configuration

Set the following variables in deploy.py file before running the script:

- `HCLOUD_TOKEN`: Your Hetzner Cloud API token.
- `YOUR_LOCAL_SSH_PUBKEY`: Your SSH public key.

## Installation

1. Clone the repository:

   ```bash
   git clone git@gitea-hetzner-setup.git
   cd gitea-hetzner-setup
