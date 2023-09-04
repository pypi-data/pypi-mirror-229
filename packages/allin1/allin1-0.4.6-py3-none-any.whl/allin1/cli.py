import argparse
import torch

from pathlib import Path
from .analyze import analyze


def make_parser():
  cwd = Path.cwd()
  parser = argparse.ArgumentParser()
  parser.add_argument('paths', nargs='+', type=Path, default=[], help='Path to tracks')
  parser.add_argument('-a', '--activ', action='store_true',
                      help='Save frame-level raw activations from sigmoid and softmax (default: False)')
  parser.add_argument('-e', '--embed', action='store_true',
                      help='Save frame-level embeddings (default: False)')
  parser.add_argument('-o', '--out-dir', type=Path, default=cwd / './struct',
                      help='Path to a directory to store analysis results (default: ./struct)')
  parser.add_argument('-v', '--visualize', action='store', nargs='?', const=True, default=False, type=str,
                      help='Save visualizations (default: False, True to save to ./viz, or specify a path)')
  parser.add_argument('-s', '--sonify', action='store', nargs='?', const=True, default=False, type=str,
                      help='Save sonifications (default: False, True to save to ./sonif, or specify a path)')
  parser.add_argument('-m', '--model', type=str, default='harmonix-all',
                      help='Name of the pretrained model to use (default: harmonix-all)')
  parser.add_argument('-d', '--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu',
                      help='Device to use (default: cuda if available else cpu)')
  parser.add_argument('-k', '--keep-byproducts', action='store_true',
                      help='Keep demixed audio files and spectrograms (default: False)')
  parser.add_argument('--demix-dir', type=Path, default=cwd / 'demix',
                      help='Path to a directory to store demixed tracks (default: ./demix)')
  parser.add_argument('--spec-dir', type=Path, default=cwd / 'spec',
                      help='Path to a directory to store spectrograms (default: ./spec)')

  return parser


def main():
  parser = make_parser()
  args = parser.parse_args()

  if not args.paths:
    raise ValueError('At least one path must be specified.')

  assert args.out_dir is not None, 'Output directory must be specified with --out-dir'

  analyze(
    paths=args.paths,
    out_dir=args.out_dir,
    visualize=args.visualize,
    sonify=args.sonify,
    model=args.model,
    device=args.device,
    include_activations=args.activ,
    include_embeddings=args.embed,
    demix_dir=args.demix_dir,
    spec_dir=args.spec_dir,
    keep_byproducts=args.keep_byproducts,
  )

  print(f'=> Analysis results are successfully saved to {args.out_dir}')


if __name__ == '__main__':
  main()
