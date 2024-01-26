from pssh.clients import ParallelSSHClient

def validate_time_string(hosts_str):
    # Regular expression to validate the format hh:mm:ss
    pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$')
    if not pattern.match(hosts_str):
        raise argparse.ArgumentTypeError(f"Invalid host number: {hosts_str} , use eg. 0")
    return hosts_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
                                    Start tmux session for each host if it has not been started yet.
                                    
                                    usage: create_session.py [-h] [-j 0 | 1 | n]
                                    """
                                    )
    
    parser.add_argument('-j', type=validate_hosts, help='Host number where session should be created', nargs='+')
    
    args = parser.parse_args()  # Parse the command-line arguments
    
    # checker function needs to return jas0, jas1
    hosts = args.j # Access list of parsed hosts

    # sshpass -p secret ssh -o StrictHostKeyChecking=no jas@$host.local 'tmux new-session -d -s $host'

    tmux_session_name = 'jas'
    ssh_username = 'jas'
    ssh_password = 'secret'

    check_tmux_session_cmd = f'tmux has-session -t {tmux_session_name} 2>/dev/null || echo "Not Found"'
    create_tmux_session_cmd = f'tmux new-session -d -s {tmux_session_name}'

    options = {'stricthostkeychecking': 'no',}
    client = ParallelSSHClient(hosts, user=ssh_username, password=ssh_password, ssh_config=options)

    output = client.run_command(check_tmux_session_cmd)

    for host, host_output in output.items():
        if 'Not Found' in host_output.stdout:
            # If the tmux session is not found, create it
            create_cmd_output = client.run_command(create_tmux_session_cmd, hosts=[host])
            print(f'Tmux session created on {host}')
        else:
            print(f'Tmux session already exists on {host}')

    client.close()
