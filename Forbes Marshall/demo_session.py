"""
Session Management Demo
Demo script to test session management functionality
"""
from utils.session_manager import SessionManager
import time

def demo_session_management():
    """Demonstrate session management features"""
    print("=== Session Management Demo ===\n")

    # Create session manager
    session_manager = SessionManager()
    print("1. SessionManager created")

    # Set shorter timeout for demo (30 seconds)
    session_manager.set_timeout(30)
    print("2. Session timeout set to 30 seconds for demo\n")

    # Create session
    print("3. Creating session for user 'admin'...")
    success = session_manager.create_session(1, "admin", "Admin")
    if success:
        print("   ✓ Session created successfully")
    else:
        print("   ✗ Failed to create session")
        return

    # Display session info
    print("\n4. Session Information:")
    session_info = session_manager.get_session_info()
    if session_info:
        print(f"   User ID: {session_info['user_id']}")
        print(f"   Username: {session_info['username']}")
        print(f"   Role: {session_info['role']}")
        print(f"   Time remaining: {session_info['time_remaining_seconds']} seconds")
        print(f"   Session duration: {session_info['session_duration_seconds']} seconds")

    # Test session validation over time
    print("\n5. Testing session validation over time...")
    for i in range(6):
        print(f"   Check {i+1}: ", end="")

        if session_manager.is_session_valid():
            time_left = session_manager.get_time_until_expiry()
            print(f"Valid - {time_left} seconds remaining")

            # Update activity
            session_manager.update_activity()

            # Show warning test
            if session_manager.should_show_warning():
                print("     ⚠️ Session timeout warning should be shown")

        else:
            print("Invalid - Session expired")
            break

        # Wait 7 seconds between checks
        time.sleep(7)

    # Test session extension
    print("\n6. Testing session extension...")
    if session_manager.is_session_valid():
        print("   Session is still valid, extending...")
        session_manager.extend_session()

        session_info = session_manager.get_session_info()
        if session_info:
            print(f"   ✓ Session extended - {session_info['time_remaining_seconds']} seconds remaining")

    # Final status
    print("\n7. Final session status:")
    if session_manager.is_session_valid():
        print("   ✓ Session is still valid")
    else:
        print("   ✗ Session has expired")

    # Cleanup
    print("\n8. Destroying session...")
    session_manager.destroy_session()
    print("   ✓ Session destroyed")

    print("\n=== Demo completed ===")

if __name__ == "__main__":
    demo_session_management()