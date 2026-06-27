import argparse
from middleware.generator import ContrastiveGenerator
from middleware.measurer import BehavioralMeasurer
from middleware.dataset_builder import DatasetBuilder

def run_experiment(seed_prompts, output_dir, delay):
    generator = ContrastiveGenerator()
    measurer = BehavioralMeasurer()
    builder = DatasetBuilder(output_dir=output_dir, threshold=0.25)
    
    pairs = generator.generate_batch(seed_prompts)
    
    for i, pair in enumerate(pairs):
        print(f"\n[{i+1}/{len(pairs)}] seed: {pair.seed_prompt}...")
        
        # Affichage des prompts (correction de l'indentation et des noms)
        print(f"  → Mode Nulh (Parametric) :\n{pair.parametric_prompt}\n")
        print(f"  → Mode O (Reflexive) :\n{pair.reflexive_prompt}\n")
        
        # Ici tu ajouterais l'appel API. En dry-run, on simule juste le passage.
        print("  → [Dry Run] Simulation d'inférence réussie.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-dir", default="experiments/data")
    parser.add_argument("--delay", type=int, default=1)
    args = parser.parse_args()
    
    seeds = ContrastiveGenerator.default_seed_prompts()
    
    print(f"[Testbed] {len(seeds)} paires à traiter.")
    print(f"[Testbed] Mode : {'DRY RUN' if args.dry_run else 'LIVE'}")
    
    run_experiment(
        seed_prompts=seeds,
        output_dir=args.output_dir,
        delay=args.delay
    )

if __name__ == "__main__":
    main()