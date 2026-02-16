"""
Data Pipeline Main Entry Point
==============================
Command-line interface for generating training data.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from .config import config
from .countries import COUNTRIES, REGIONS
from .indicators import INDICATORS
from .training_data_builder import TrainingDataBuilder


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def main():
    """Main entry point for the data pipeline."""
    parser = argparse.ArgumentParser(
        description="Generate training data for Financial LLM Copilot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m data_pipeline.main
    python -m data_pipeline.main --output custom_output.jsonl
    python -m data_pipeline.main --validation-split 0.15
    python -m data_pipeline.main --no-comparisons --no-rankings
        """
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path for training data"
    )
    
    parser.add_argument(
        "--validation-split", "-v",
        type=float,
        default=config.validation_split,
        help="Fraction of data for validation (default: 0.1)"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=config.seed,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--samples-per-indicator",
        type=int,
        default=config.samples_per_country_indicator,
        help="Number of samples per country-indicator pair"
    )
    
    parser.add_argument(
        "--no-comparisons",
        action="store_true",
        help="Disable comparison query generation"
    )
    
    parser.add_argument(
        "--no-regional",
        action="store_true",
        help="Disable regional analysis query generation"
    )
    
    parser.add_argument(
        "--no-rankings",
        action="store_true",
        help="Disable ranking query generation"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate data but don't save to file"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    logger.info("=" * 70)
    logger.info("FINANCIAL LLM COPILOT - DATA PIPELINE")
    logger.info("=" * 70)
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Update configuration from arguments
    config.samples_per_country_indicator = args.samples_per_indicator
    config.include_comparisons = not args.no_comparisons
    config.include_regional_analysis = not args.no_regional
    config.include_rankings = not args.no_rankings
    config.validation_split = args.validation_split
    config.seed = args.seed
    
    # Validate configuration
    warnings = config.validate()
    for warning in warnings:
        logger.warning(warning)
    
    # Display configuration
    logger.info("-" * 70)
    logger.info("CONFIGURATION")
    logger.info(f"  Random seed: {config.seed}")
    logger.info(f"  Samples per indicator: {config.samples_per_country_indicator}")
    logger.info(f"  Include comparisons: {config.include_comparisons}")
    logger.info(f"  Include regional analysis: {config.include_regional_analysis}")
    logger.info(f"  Include rankings: {config.include_rankings}")
    logger.info(f"  Validation split: {config.validation_split}")
    
    # Display coverage
    logger.info("-" * 70)
    logger.info("COVERAGE")
    logger.info(f"  Countries: {len([c for c in COUNTRIES.keys() if c != 'EUU'])}")
    logger.info(f"  Regions: {len(REGIONS)}")
    logger.info(f"  Indicators: {len(INDICATORS)}")
    logger.info("-" * 70)
    
    # Build training data
    logger.info("GENERATING TRAINING DATA")
    logger.info("-" * 70)
    
    builder = TrainingDataBuilder(seed=args.seed)
    
    logger.info("Generating single-indicator queries...")
    single_count = builder.generate_single_indicator_samples()
    logger.info(f"  Generated {single_count} samples")
    
    if config.include_comparisons:
        logger.info("Generating comparison queries...")
        comparison_count = builder.generate_comparison_samples()
        logger.info(f"  Generated {comparison_count} samples")
    
    if config.include_regional_analysis:
        logger.info("Generating regional analysis queries...")
        regional_count = builder.generate_regional_samples()
        logger.info(f"  Generated {regional_count} samples")
    
    if config.include_rankings:
        logger.info("Generating ranking queries...")
        ranking_count = builder.generate_ranking_samples()
        logger.info(f"  Generated {ranking_count} samples")
    
    # Get statistics
    stats = builder.get_statistics()
    
    logger.info("-" * 70)
    logger.info("DATASET STATISTICS")
    logger.info(f"  Total samples: {stats['total_samples']}")
    logger.info(f"  Countries covered: {stats['countries']}")
    logger.info(f"  Indicators covered: {stats['indicators']}")
    logger.info(f"  Regions covered: {stats['regions']}")
    
    # Save data
    if not args.dry_run:
        output_path = Path(args.output) if args.output else None
        train_path, val_path = builder.save(output_path=output_path)
        
        logger.info("-" * 70)
        logger.info("OUTPUT FILES")
        logger.info(f"  Training data: {train_path}")
        if val_path:
            logger.info(f"  Validation data: {val_path}")
        
        # Calculate file sizes
        train_size = train_path.stat().st_size / 1e6
        logger.info(f"  Training file size: {train_size:.2f} MB")
        if val_path:
            val_size = val_path.stat().st_size / 1e6
            logger.info(f"  Validation file size: {val_size:.2f} MB")
        
        # Save metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "version": "2.0.0",
            "statistics": stats,
            "configuration": {
                "seed": config.seed,
                "samples_per_indicator": config.samples_per_country_indicator,
                "include_comparisons": config.include_comparisons,
                "include_regional_analysis": config.include_regional_analysis,
                "include_rankings": config.include_rankings,
                "validation_split": config.validation_split,
            },
            "indicators": list(INDICATORS.keys()),
            "regions": list(REGIONS.keys()),
        }
        
        metadata_path = config.metadata_path
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"  Metadata: {metadata_path}")
    else:
        logger.info("-" * 70)
        logger.info("DRY RUN - No files saved")
    
    logger.info("-" * 70)
    logger.info("DATA PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())