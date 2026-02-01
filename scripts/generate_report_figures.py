"""
Generate all visualization figures for Tasks 1 & 2 report
Saves both HTML (interactive) and PNG (static) versions
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.utils.config import config
from src.analysis.eda import EDAAnalyzer
from src.analysis.visualizer import DataVisualizer

logger = get_logger(__name__)


def generate_all_figures():
    """Generate all visualization figures for the report"""
    figures_dir = config.reports_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("Generating Report Figures for Tasks 1 & 2")
    logger.info("=" * 80)
    
    eda_analyzer = EDAAnalyzer()
    visualizer = DataVisualizer(eda_analyzer)
    
    figures_generated = []
    
    # Figure 1: Access Trajectory
    logger.info("\nGenerating Figure 1: Access Trajectory...")
    try:
        fig = visualizer.plot_access_trajectory(
            save_path=figures_dir / "access_trajectory.html",
            show_events=True
        )
        if fig:
            try:
                fig.write_image(figures_dir / "access_trajectory.png", width=1200, height=600)
                logger.info(f"✓ Saved: {figures_dir / 'access_trajectory.png'}")
                figures_generated.append("access_trajectory.png")
            except Exception as e:
                logger.warning(f"Could not save PNG (kaleido may not be installed): {e}")
                logger.info("HTML version saved")
    except Exception as e:
        logger.error(f"Error generating access trajectory: {e}")
    
    # Figure 2: Usage Trends
    logger.info("\nGenerating Figure 2: Usage Trends...")
    try:
        fig = visualizer.plot_usage_trends(
            save_path=figures_dir / "usage_trends.html"
        )
        if fig:
            try:
                fig.write_image(figures_dir / "usage_trends.png", width=1200, height=600)
                logger.info(f"✓ Saved: {figures_dir / 'usage_trends.png'}")
                figures_generated.append("usage_trends.png")
            except Exception as e:
                logger.warning(f"Could not save PNG: {e}")
    except Exception as e:
        logger.error(f"Error generating usage trends: {e}")
    
    # Figure 3: Event Timeline
    logger.info("\nGenerating Figure 3: Event Timeline...")
    try:
        fig = visualizer.plot_event_timeline(
            save_path=figures_dir / "event_timeline.html"
        )
        if fig:
            try:
                fig.write_image(figures_dir / "event_timeline.png", width=1400, height=400)
                logger.info(f"✓ Saved: {figures_dir / 'event_timeline.png'}")
                figures_generated.append("event_timeline.png")
            except Exception as e:
                logger.warning(f"Could not save PNG: {e}")
    except Exception as e:
        logger.error(f"Error generating event timeline: {e}")
    
    # Figure 4: Correlation Heatmap
    logger.info("\nGenerating Figure 4: Correlation Heatmap...")
    try:
        fig = visualizer.plot_correlation_heatmap(
            save_path=figures_dir / "correlation_heatmap.html"
        )
        if fig:
            try:
                fig.write_image(figures_dir / "correlation_heatmap.png", width=1000, height=1000)
                logger.info(f"✓ Saved: {figures_dir / 'correlation_heatmap.png'}")
                figures_generated.append("correlation_heatmap.png")
            except Exception as e:
                logger.warning(f"Could not save PNG: {e}")
    except Exception as e:
        logger.error(f"Error generating correlation heatmap: {e}")
    
    # Figure 5: Temporal Coverage
    logger.info("\nGenerating Figure 5: Temporal Coverage...")
    try:
        fig = visualizer.plot_temporal_coverage(
            save_path=figures_dir / "temporal_coverage.html"
        )
        if fig:
            try:
                fig.write_image(figures_dir / "temporal_coverage.png", width=1200, height=800)
                logger.info(f"✓ Saved: {figures_dir / 'temporal_coverage.png'}")
                figures_generated.append("temporal_coverage.png")
            except Exception as e:
                logger.warning(f"Could not save PNG: {e}")
    except Exception as e:
        logger.error(f"Error generating temporal coverage: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info(f"Figure generation complete. Generated {len(figures_generated)} PNG files:")
    for fig in figures_generated:
        logger.info(f"  - {figures_dir / fig}")
    logger.info("=" * 80)
    
    return figures_generated


if __name__ == "__main__":
    generate_all_figures()
