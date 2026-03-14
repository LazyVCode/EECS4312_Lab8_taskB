## Student Name: Vikram Singh Chauhan
## Student ID: 220914867

"""
Task B: Event Registration with Waitlist (Stub)
In this lab, you will design and implement an Event Registration with Waitlist system using an LLM assistant as your primary programming collaborator. 
You are asked to implement a Python module that manages registration for a single event with a fixed capacity. 
The system must:
•	Accept a fixed capacity.
•	Register users until capacity is reached.
•	Place additional users into a FIFO waitlist.
•	Automatically promote the earliest waitlisted user when a registered user cancels.
•	Prevent duplicate registrations.
•	Allow users to query their current status.

The system must ensure that:
•	The number of registered users never exceeds capacity.
•	Waitlist ordering preserves FIFO behavior.
•	Promotions occur deterministically under identical operation sequences.

The module must preserve the following invariants:
•	A user may not appear more than once in the system.
•	A user may not simultaneously exist in multiple states.
•	The system state must remain consistent after every operation.

The system must correctly handle non-trivial scenarios such as:
•	Multiple cancellations in sequence.
•	Users attempting to re-register after canceling.
•	Waitlisted users canceling before promotion.
•	Capacity equal to zero.
•	Simultaneous or rapid consecutive operations.
•	Queries during state transitions.

The output consists of the updated registration state and ordered lists of registered and waitlisted users after each operation.
"""
"""
Updated for Lab 9 - Persona Constraints (Jane and Mo)
"""

from dataclasses import dataclass
from typing import List, Optional

class DuplicateRequest(Exception):
    """Raised if a user tries to register but is already registered or waitlisted."""
    pass

class NotFound(Exception):
    """Raised if a user cannot be found for cancellation."""
    pass

@dataclass(frozen=True)
class UserStatus:
    """
    state:
      - "registered"
      - "waitlisted"
      - "none"
    position: 1-based waitlist position if waitlisted; otherwise None
    """
    state: str
    position: Optional[int] = None


class EventRegistration:
    """
    Event Registration module managing capacity, FIFO waitlists, and state transitions.
    Updated to support Persona constraints (deterministic behavior, explicit notifications, avoiding silent failures).
    """

    def __init__(self, capacity: int) -> None:
        """
        Args:
            capacity: maximum number of registered users (>= 0)
        """
        self.capacity = capacity
        self.registered_users: List[str] = []
        self.waitlisted_users: List[str] = []

    def register(self, user_id: str) -> UserStatus:
        """
        Register a user:
          - if capacity available -> registered
          - else -> waitlisted (FIFO)
        
        Constraint C5 (Jane): Returns concise status output to prevent notification spam.
        Constraint C4 (Mo): Explicitly rejects duplicates instead of silently ignoring.

        Raises:
            DuplicateRequest if user already exists (registered or waitlisted)
        """
        if user_id in self.registered_users or user_id in self.waitlisted_users:
            # Explicit error reason for Mo
            raise DuplicateRequest(f"Registration Rejected: User '{user_id}' is already registered or waitlisted.")

        if len(self.registered_users) < self.capacity:
            self.registered_users.append(user_id)
            return UserStatus("registered")
        else:
            self.waitlisted_users.append(user_id)
            return UserStatus("waitlisted", len(self.waitlisted_users))

    def cancel(self, user_id: str) -> Optional[str]:
        """
        Cancel a user:
          - if registered -> remove and promote earliest waitlisted user (if any)
          - if waitlisted -> remove from waitlist
          - if not found -> raise NotFound
        
        Constraint C3 (Mo): Returns an explicit explanation notification if a waitlist promotion occurs.
        Constraint C4 (Mo): Explicitly raises an error if the user is not found to avoid silent failures.
        """
        if user_id in self.registered_users:
            self.registered_users.remove(user_id)
            
            # Promote the earliest waitlisted user if there's room and someone is waiting
            if self.waitlisted_users and len(self.registered_users) < self.capacity:
                promoted_user = self.waitlisted_users.pop(0)
                self.registered_users.append(promoted_user)
                
                # C3 (Mo): Explicit explanation of waitlist promotion returned to the system
                return f"Notification: User '{promoted_user}' was automatically promoted to registered status due to a cancellation."
            
            # C5 (Jane): Return nothing if no automated promotion happened to avoid spam
            return None 

        elif user_id in self.waitlisted_users:
            self.waitlisted_users.remove(user_id)
            return None

        else:
            # C4 (Mo): Avoid silent failure on non-existent user cancellation
            raise NotFound(f"Cancellation Failed: User '{user_id}' does not exist in the system.")

    def status(self, user_id: str) -> UserStatus:
        """
        Return status of a user:
          - registered
          - waitlisted with position (1-based)
          - none
        
        Constraint C1/C5: Accurately reflects exact FIFO position cleanly.
        """
        if user_id in self.registered_users:
            return UserStatus("registered")
        if user_id in self.waitlisted_users:
            position = self.waitlisted_users.index(user_id) + 1
            return UserStatus("waitlisted", position)
        
        return UserStatus("none")

    def snapshot(self) -> dict:
        """
        Return a deterministic snapshot of internal state.
        """
        return {
            "registered": list(self.registered_users),
            "waitlist": list(self.waitlisted_users)
        }
