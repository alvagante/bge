#!/usr/bin/env python3
"""
Quick test script to verify utility modules work correctly.
"""

from src.utils import get_logger, ErrorHandler, SummaryReporter, Validator, ValidationError, EpisodeResult

def test_utilities():
    """Test all utility modules."""
    print("Testing utility modules...")
    print("-" * 60)
    
    # Test logger
    print("\n1. Testing Logger...")
    logger = get_logger(log_level='INFO', file_output=False)
    logger.info('Logger initialized successfully')
    logger.debug('This debug message should not appear')
    logger.warning('This is a warning')
    logger.error('This is an error')
    print("✓ Logger test passed")
    
    # Test error handler
    print("\n2. Testing Error Handler...")
    error_handler = ErrorHandler(logger)
    error_handler.handle_extraction_error('1', 'Test extraction error')
    error_handler.handle_generation_error('2', 'instagram', 'Test generation error')
    error_handler.handle_publishing_error('3', 'twitter', 'Test publishing error')
    print(f"✓ Error handler test passed - {error_handler.get_error_count()} errors recorded")
    
    # Print error summary
    print("\n3. Testing Error Summary...")
    error_handler.print_summary()
    print("✓ Error summary test passed")
    
    # Test summary reporter
    print("\n4. Testing Summary Reporter...")
    reporter = SummaryReporter(logger)
    reporter.start_execution()
    
    # Add some test results
    result1 = EpisodeResult(
        episode_number="1",
        success=True,
        images_generated=2,
        posts_published=1,
        platforms=["instagram", "twitter"]
    )
    reporter.add_episode_result(result1)
    
    result2 = EpisodeResult(
        episode_number="2",
        success=False,
        images_generated=1,
        images_failed=1,
        errors=["Failed to load template"]
    )
    reporter.add_episode_result(result2)
    
    reporter.end_execution()
    reporter.print_quick_summary()
    print("✓ Summary reporter test passed")
    
    # Test validator
    print("\n5. Testing Validator...")
    validator = Validator(logger)
    
    # Test episode number validation
    try:
        validator.validate_episode_number('42')
        print("✓ Valid episode number accepted")
    except ValidationError as e:
        print(f"✗ Validator test failed: {e}")
        return False
    
    # Test invalid episode number
    try:
        validator.validate_episode_number('invalid')
        print("✗ Invalid episode number should have been rejected")
        return False
    except ValidationError:
        print("✓ Invalid episode number rejected")
    
    # Test color validation
    try:
        validator.validate_color('#FFFFFF')
        validator.validate_color('#FFF')
        print("✓ Valid colors accepted")
    except ValidationError as e:
        print(f"✗ Color validation failed: {e}")
        return False
    
    # Test invalid color
    try:
        validator.validate_color('white')
        print("✗ Invalid color should have been rejected")
        return False
    except ValidationError:
        print("✓ Invalid color rejected")
    
    # Test image dimensions
    try:
        validator.validate_image_dimensions(1080, 1080)
        print("✓ Valid image dimensions accepted")
    except ValidationError as e:
        print(f"✗ Dimension validation failed: {e}")
        return False
    
    # Test text sanitization
    sanitized = validator.sanitize_text("Hello\x00World\nTest")
    print(f"✓ Text sanitization works: '{sanitized}'")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_utilities()
    exit(0 if success else 1)
