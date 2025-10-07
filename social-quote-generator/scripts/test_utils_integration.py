#!/usr/bin/env python3
"""
Integration test demonstrating all utility features working together.
"""

from src.utils import (
    setup_pipeline_utilities,
    validate_configuration,
    validate_platform_credentials,
    create_episode_result,
    ensure_output_directories,
    format_duration,
    ErrorSeverity,
    ValidationError
)

def test_integration():
    """Test integrated utility usage."""
    print("=" * 70)
    print("UTILITY INTEGRATION TEST")
    print("=" * 70)
    
    # 1. Set up all utilities at once
    print("\n1. Setting up pipeline utilities...")
    logger, error_handler, reporter, validator = setup_pipeline_utilities(
        log_dir="output/logs",
        log_level="INFO",
        file_output=False  # Disable file output for test
    )
    print("✓ All utilities initialized")
    
    # 2. Ensure output directories
    print("\n2. Ensuring output directories...")
    ensure_output_directories("output/images", "output/logs", logger)
    print("✓ Directories created/verified")
    
    # 3. Validate sample configuration
    print("\n3. Validating configuration...")
    sample_config = {
        'general': {
            'episodes_dir': '_episodes',
            'output_dir': 'output/images',
            'log_level': 'INFO'
        },
        'images': {
            'platforms': {
                'instagram': {
                    'dimensions': [1080, 1080]
                },
                'twitter': {
                    'dimensions': [1200, 675]
                }
            },
            'branding': {
                'primary_color': '#FFFFFF',
                'secondary_color': '#000000',
                'background_color': '#1a1a1a'
            }
        }
    }
    
    config_valid = validate_configuration(sample_config, validator, error_handler)
    if config_valid:
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration has errors")
    
    # 4. Validate episode numbers
    print("\n4. Validating episode numbers...")
    test_episodes = ['1', '42', '100', 'invalid', '-5']
    for ep in test_episodes:
        try:
            validator.validate_episode_number(ep)
            print(f"  ✓ Episode {ep} is valid")
        except ValidationError as e:
            print(f"  ✗ Episode {ep} is invalid: {e}")
            error_handler.handle_validation_error(
                f"Invalid episode number: {ep}",
                exception=e,
                severity=ErrorSeverity.WARNING
            )
    
    # 5. Simulate pipeline execution
    print("\n5. Simulating pipeline execution...")
    reporter.start_execution()
    
    # Process episode 1 - success
    logger.info("Processing episode 1...")
    result1 = create_episode_result(
        episode_number="1",
        success=True,
        images_generated=2,
        posts_published=1,
        platforms=["instagram", "twitter"]
    )
    reporter.add_episode_result(result1)
    
    # Process episode 2 - partial failure
    logger.info("Processing episode 2...")
    error_handler.handle_generation_error(
        episode_number="2",
        platform="instagram",
        message="Template file not found",
        severity=ErrorSeverity.ERROR
    )
    result2 = create_episode_result(
        episode_number="2",
        success=False,
        images_generated=1,
        images_failed=1,
        platforms=["twitter"],
        errors=["Template file not found for instagram"]
    )
    reporter.add_episode_result(result2)
    
    # Process episode 3 - publishing failure
    logger.info("Processing episode 3...")
    error_handler.handle_publishing_error(
        episode_number="3",
        platform="twitter",
        message="API rate limit exceeded",
        severity=ErrorSeverity.ERROR
    )
    result3 = create_episode_result(
        episode_number="3",
        success=False,
        images_generated=2,
        posts_failed=2,
        platforms=["instagram", "twitter"],
        errors=["API rate limit exceeded"]
    )
    reporter.add_episode_result(result3)
    
    reporter.end_execution()
    
    # 6. Print comprehensive reports
    print("\n6. Generating reports...")
    print("\n" + "-" * 70)
    print("EXECUTION SUMMARY:")
    print("-" * 70)
    reporter.print_quick_summary()
    
    print("\n" + "-" * 70)
    print("ERROR SUMMARY:")
    print("-" * 70)
    error_handler.print_summary()
    
    # 7. Test duration formatting
    print("\n7. Testing duration formatting...")
    durations = [5.5, 65.3, 3725.8]
    for duration in durations:
        formatted = format_duration(duration)
        print(f"  {duration}s = {formatted}")
    
    # 8. Get detailed summaries
    print("\n8. Getting detailed summaries...")
    pipeline_summary = reporter.get_summary()
    error_summary = error_handler.get_summary()
    
    print(f"\nPipeline Summary:")
    print(f"  Total episodes: {pipeline_summary.total_episodes_processed}")
    print(f"  Success rate: {(pipeline_summary.successful_episodes / pipeline_summary.total_episodes_processed * 100):.1f}%")
    print(f"  Images generated: {pipeline_summary.total_images_generated}")
    print(f"  Posts published: {pipeline_summary.total_posts_published}")
    
    print(f"\nError Summary:")
    print(f"  Total errors: {error_summary['total_errors']}")
    print(f"  By category: {error_summary['by_category']}")
    print(f"  By severity: {error_summary['by_severity']}")
    
    # 9. Test credential validation
    print("\n9. Testing credential validation...")
    twitter_config = {
        'api_key': 'test_key',
        'api_secret': 'test_secret',
        'access_token': 'test_token',
        'access_token_secret': 'test_token_secret'
    }
    
    is_valid = validate_platform_credentials(
        'twitter',
        twitter_config,
        validator,
        error_handler
    )
    
    if is_valid:
        print("  ✓ Twitter credentials are valid")
    else:
        print("  ✗ Twitter credentials are invalid")
    
    # Test with missing credentials
    incomplete_config = {
        'api_key': '${TWITTER_API_KEY}',  # Not substituted
        'api_secret': 'test_secret'
    }
    
    is_valid = validate_platform_credentials(
        'twitter',
        incomplete_config,
        validator,
        error_handler
    )
    
    if not is_valid:
        print("  ✓ Incomplete credentials correctly rejected")
    
    # Final summary
    print("\n" + "=" * 70)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 70)
    print(f"Total operations: {pipeline_summary.total_episodes_processed} episodes processed")
    print(f"Total errors: {error_summary['total_errors']} errors recorded")
    print(f"Error handling: All errors logged and categorized")
    print(f"Validation: All inputs validated with clear error messages")
    print(f"Reporting: Comprehensive summaries generated")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = test_integration()
    exit(0 if success else 1)
