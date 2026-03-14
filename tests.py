import pytest
from solution import EventRegistration, UserStatus, DuplicateRequest, NotFound
# Covers C1, AC1, AC6
def test_waitlist_fifo_ordering_and_status():
    """
    Standard test: Ensures users are added to the waitlist in FIFO order 
    and that their status accurately reflects their 1-based position.
    """
    er = EventRegistration(capacity=2)
    # Fill capacity
    er.register("u1")
    er.register("u2")
    # Overflow to waitlist
    s3 = er.register("u3")
    s4 = er.register("u4")
    assert s3 == UserStatus("waitlisted", 1)
    assert s4 == UserStatus("waitlisted", 2)
    # Check status method
    assert er.status("u3") == UserStatus("waitlisted", 1)
    assert er.status("u4") == UserStatus("waitlisted", 2)
# Covers C2, C3, AC1, AC2
def test_automatic_promotion_with_explicit_explanation():
    """
    Standard test: Ensures cancelling a registered user automatically promotes 
    the first waitlisted user (Jane) AND returns an explicit explanation string (Mo).
    """
    er = EventRegistration(capacity=1)
    er.register("u1")
    er.register("u2") # Waitlisted position 1
    # Cancel u1, should promote u2 and return an explicit notification
    result = er.cancel("u1")
    assert result == "Notification: User 'u2' was automatically promoted to registered status due to a cancellation."
    assert er.status("u1") == UserStatus("none")
    assert er.status("u2") == UserStatus("registered")
# Covers C5, AC4
def test_concise_outputs_without_spam():
    """
    Standard test: Ensures operations that do NOT trigger automatic conflict resolution 
    return concise objects or None, preventing notification spam (Jane).
    """
    er = EventRegistration(capacity=2)
    # Registration returns concise dataclass, not a verbose string
    s1 = er.register("u1")
    assert s1 == UserStatus("registered")
    er.register("u2") # Waitlisted
    # Cancelling a waitlisted user does not promote anyone, so it should return None
    cancel_result = er.cancel("u2")
    assert cancel_result is None
# Edge Case Tests
# Covers C4, AC3 (Edge Case)
def test_cancel_nonexistent_user_raises_notfound_with_explanation():
    """
    Edge case: Cancelling a user that doesn't exist. 
    Ensures the system does not fail silently and provides a clear error (Mo).
    """
    er = EventRegistration(capacity=1)
    with pytest.raises(NotFound) as excinfo:
        er.cancel("ghost_user")
    assert "Cancellation Failed: User 'ghost_user' does not exist in the system." in str(excinfo.value)
# Covers C4, AC4 (Edge Case)
def test_duplicate_registration_explicit_rejection():
    """
    Edge case: Attempting to register the same user twice.
    Ensures the system explicitly rejects the action with a clear reason instead of ignoring it (Mo).
    """
    er = EventRegistration(capacity=2)
    er.register("u1")
    with pytest.raises(DuplicateRequest) as excinfo:
        er.register("u1")
    assert "Registration Rejected: User 'u1' is already registered or waitlisted." in str(excinfo.value)
# Covers C1, C2, C3, AC1, AC2 (Edge Case)
def test_multiple_rapid_cancellations():
    """
    Edge case: Multiple sequential cancellations.
    Ensures the FIFO queue remains stable and outputs multiple correct notifications.
    """
    er = EventRegistration(capacity=2)
    # Register 2, Waitlist 3
    for i in range(1, 6):
        er.register(f"u{i}")  
    # Cancel the two registered users
    res1 = er.cancel("u1") # Should promote u3
    res2 = er.cancel("u2") # Should promote u4
    assert res1 == "Notification: User 'u3' was automatically promoted to registered status due to a cancellation."
    assert res2 == "Notification: User 'u4' was automatically promoted to registered status due to a cancellation."
    # Check final state: u3 and u4 registered, u5 is now 1st on waitlist
    snap = er.snapshot()
    assert snap["registered"] == ["u3", "u4"]
    assert snap["waitlist"] == ["u5"]
    assert er.status("u5") == UserStatus("waitlisted", 1)
