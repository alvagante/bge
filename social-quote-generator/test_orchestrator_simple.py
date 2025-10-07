#!/usr/bin/env python3
"""Simple test for orchestrator structure and imports."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing orchestrator module structure...")

try:
    # Test imports
    print("\n1. Testing imports...")
    from src.orchestrator import (
        EpisodeResult,
        PipelineResult,
        PipelineOrchestrator
    )
    print("   ✓ All classes imported successfully")
    
    # Test dataclass creation
    print("\n2. Testing EpisodeResult dataclass...")
    episode_result = EpisodeResult(
        episode_number="1",
        success=True
    )
    print(f"   ✓ Created EpisodeResult: {episode_result.episode_number}")
    print(f"   ✓ has_errors: {episode_result.has_errors}")
    print(f"   ✓ images_generated: {episode_result.images_generated}")
    print(f"   ✓ posts_published: {episode_result.posts_published}")
    
    # Test PipelineResult
    print("\n3. Testing PipelineResult dataclass...")
    from datetime import datetime
    start = datetime.now()
    end = datetime.now()
    
    pipeline_result = PipelineResult(
        total_episodes=1,
        successful_images=1,
        failed_images=0,
        successful_posts=0,
        failed_posts=0,
        results=[episode_result],
        start_time=start,
        end_time=end
    )
    print(f"   ✓ Created PipelineResult")
    print(f"   ✓ total_episodes: {pipeline_result.total_episodes}")
    print(f"   ✓ success_rate: {pipeline_result.success_rate:.1f}%")
    print(f"   ✓ duration: {pipeline_result.duration:.4f}s")
    
    # Test summary generation
    print("\n4. Testing summary generation...")
    summary = pipeline_result.get_summary()
    print("   ✓ Summary generated:")
    for line in summary.split('\n')[:5]:
        print(f"     {line}")
    
    print("\n" + "=" * 60)
    print("✓ All orchestrator structure tests passed!")
    print("=" * 60)
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
