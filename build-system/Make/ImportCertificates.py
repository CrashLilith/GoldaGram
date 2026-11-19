import os
import sys
import argparse
import shlex

from BuildEnvironment import run_executable_with_output

def import_certificates(certificatesPath):
    if not os.path.exists(certificatesPath):
        print('{} does not exist'.format(certificatesPath))
        sys.exit(1)

    keychain_name = 'temp.keychain'
    keychain_password = 'secret'

    existing_keychains = run_executable_with_output('security', arguments=['list-keychains'], check_result=True)
    keychain_paths = shlex.split(existing_keychains)
    if any(os.path.basename(path).startswith(keychain_name) for path in keychain_paths):
        # The keychain name is required. Without it `security` fails with
        # "SecKeychainDelete: The specified keychain is not a valid keychain file",
        # which only happens on a second build inside one VM -- unreachable while every
        # build got a fresh ephemeral VM, and hit on every reuse of a persistent one.
        run_executable_with_output('security', arguments=['delete-keychain', keychain_name], check_result=True)

    run_executable_with_output('security', arguments=[
        'create-keychain',
        '-p',
        keychain_password,
        keychain_name
    ], check_result=True)

    existing_keychains = run_executable_with_output('security', arguments=['list-keychains', '-d', 'user'])
    keychain_paths = shlex.split(existing_keychains)

    run_executable_with_output('security', arguments=[
        'list-keychains',
        '-d',
        'user',
        '-s',
        keychain_name,
        *keychain_paths
    ], check_result=True)

    run_executable_with_output('security', arguments=['set-keychain-settings', keychain_name])
    run_executable_with_output('security', arguments=['unlock-keychain', '-p', keychain_password, keychain_name])

    for file_name in os.listdir(certificatesPath):
        file_path = certificatesPath + '/' + file_name
        if file_path.endswith('.p12') or file_path.endswith('.cer'):
            run_executable_with_output('security', arguments=[
                'import',
                file_path,
                '-k',
                keychain_name,
                '-P',
                '',
                '-T',
                '/usr/bin/codesign',
                '-T',
                '/usr/bin/security'
            ], check_result=file_path.endswith('.p12'))
            if file_name == 'Public.cer':
                # The fake signing certificate is self-signed. Importing it
                # alone does not make macOS recognize it as a codesigning
                # identity, so trust it in this temporary build keychain.
                run_executable_with_output('security', arguments=[
                    'add-trusted-cert', '-r', 'trustRoot', '-k', keychain_name, file_path
                ], check_result=True)

    run_executable_with_output('security', arguments=[
        'import',
        'build-system/AppleWWDRCAG3.cer',
        '-k',
        keychain_name,
        '-P',
        '',
        '-T',
        '/usr/bin/codesign',
        '-T',
        '/usr/bin/security'
    ], check_result=False)

    run_executable_with_output('security', arguments=[
        'set-key-partition-list',
        '-S',
        'apple-tool:,apple:',
        '-k',
        keychain_password,
        keychain_name
    ], check_result=True)

    identities = run_executable_with_output('security', arguments=[
        'find-identity', '-v', '-p', 'codesigning', keychain_name
    ], check_result=True)
    if 'valid identities found' not in identities or '0 valid identities found' in identities:
        print('No valid code-signing identity was imported into {}'.format(keychain_name))
        print(identities)
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='build')

    parser.add_argument(
        '--path',
        required=True,
        help='Path to certificates.'
    )

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    import_certificates(args.path)
