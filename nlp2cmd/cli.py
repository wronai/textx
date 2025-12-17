#!/usr/bin/env python3
"""
NLP2CMD CLI - Prosty interfejs linii komend.

Użycie:
    nlp2cmd-cli bash "pokaż pliki"
    nlp2cmd-cli env "ustaw PORT na 8080"
    nlp2cmd-cli docker "uruchom postgres"
"""

import argparse
import sys
import logging
from nlp2cmd import Text2Env, Text2Bash, Text2Makefile, Text2Docker, Pipeline


def setup_logging(verbose: bool):
    """Konfiguracja logowania"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def cmd_bash(args):
    """Komenda bash"""
    bash = Text2Bash(
        safe_mode=not args.unsafe,
        dry_run=args.dry_run,
        model_name=args.model if args.model else None
    )
    
    result = bash.execute(args.command)
    
    if result.success:
        print(f"✓ {result.command}")
        if result.output and not args.dry_run:
            print(result.output)
        return 0
    else:
        print(f"✗ Error: {result.error}", file=sys.stderr)
        return 1


def cmd_env(args):
    """Komenda env"""
    env = Text2Env(
        env_file=args.file,
        backup=args.backup,
        dry_run=args.dry_run
    )
    
    result = env.execute(args.command)
    
    if result.success:
        print(f"✓ {result.output or result.command}")
        return 0
    else:
        print(f"✗ Error: {result.error}", file=sys.stderr)
        return 1


def cmd_make(args):
    """Komenda make"""
    make = Text2Makefile(
        makefile=args.file,
        dry_run=args.dry_run
    )
    
    result = make.execute(args.command)
    
    if result.success:
        print(f"✓ {result.command}")
        if result.output and not args.dry_run:
            print(result.output)
        return 0
    else:
        print(f"✗ Error: {result.error}", file=sys.stderr)
        return 1


def cmd_docker(args):
    """Komenda docker"""
    docker = Text2Docker(
        dry_run=args.dry_run
    )
    
    result = docker.execute(args.command)
    
    if result.success:
        print(f"✓ {result.command}")
        if result.output and not args.dry_run:
            print(result.output)
        return 0
    else:
        print(f"✗ Error: {result.error}", file=sys.stderr)
        return 1


def cmd_pipeline(args):
    """Komenda pipeline"""
    # Parse steps from file or args
    if args.file:
        with open(args.file) as f:
            import yaml
            config = yaml.safe_load(f)
            steps = [(s['module'], s['command']) for s in config['steps']]
    else:
        print("Error: Pipeline wymaga pliku konfiguracyjnego", file=sys.stderr)
        return 1
    
    # Setup pipeline
    pipeline = Pipeline()
    pipeline.add_module("bash", Text2Bash(dry_run=args.dry_run))
    pipeline.add_module("env", Text2Env(dry_run=args.dry_run))
    pipeline.add_module("docker", Text2Docker(dry_run=args.dry_run))
    pipeline.add_module("make", Text2Makefile(dry_run=args.dry_run))
    
    # Execute
    results = pipeline.execute(steps)
    
    # Display results
    for i, result in enumerate(results, 1):
        status = "✓" if result.success else "✗"
        print(f"{i}. {status} {result.command}")
    
    # Summary
    summary = pipeline.get_summary()
    print(f"\nSukces: {summary['successful']}/{summary['total_executions']}")
    
    return 0 if summary['failed'] == 0 else 1


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='NLP2CMD - Natural Language to Command',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady:
  nlp2cmd-cli bash "pokaż pliki"
  nlp2cmd-cli bash "znajdź wszystkie pliki txt" --model phi-2
  nlp2cmd-cli env "ustaw PORT na 8080" --file .env
  nlp2cmd-cli docker "uruchom postgres" --dry-run
  nlp2cmd-cli pipeline --file workflow.yaml
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode (no execution)')
    
    subparsers = parser.add_subparsers(dest='module', help='Module to use')
    
    # Bash subcommand
    bash_parser = subparsers.add_parser('bash', help='Bash command generation')
    bash_parser.add_argument('command', help='Natural language command')
    bash_parser.add_argument('--model', help='LLM model to use')
    bash_parser.add_argument('--unsafe', action='store_true',
                           help='Disable safety checks')
    bash_parser.set_defaults(func=cmd_bash)
    
    # Env subcommand
    env_parser = subparsers.add_parser('env', help='Environment file management')
    env_parser.add_argument('command', help='Natural language command')
    env_parser.add_argument('--file', default='.env', help='Env file path')
    env_parser.add_argument('--no-backup', dest='backup',
                          action='store_false', help='No backup')
    env_parser.set_defaults(func=cmd_env)
    
    # Make subcommand
    make_parser = subparsers.add_parser('make', help='Makefile execution')
    make_parser.add_argument('command', help='Natural language command')
    make_parser.add_argument('--file', default='Makefile', help='Makefile path')
    make_parser.set_defaults(func=cmd_make)
    
    # Docker subcommand
    docker_parser = subparsers.add_parser('docker', help='Docker management')
    docker_parser.add_argument('command', help='Natural language command')
    docker_parser.set_defaults(func=cmd_docker)
    
    # Pipeline subcommand
    pipeline_parser = subparsers.add_parser('pipeline', help='Execute pipeline')
    pipeline_parser.add_argument('--file', required=True,
                               help='Pipeline config file (YAML)')
    pipeline_parser.set_defaults(func=cmd_pipeline)
    
    # Parse args
    args = parser.parse_args()
    
    if not args.module:
        parser.print_help()
        return 1
    
    # Setup
    setup_logging(args.verbose)
    
    # Execute
    try:
        return args.func(args)
    except Exception as e:
        print(f"✗ Fatal error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
