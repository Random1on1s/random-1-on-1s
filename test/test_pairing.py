import unittest

from pairing import generate_pairs
from pairing import Participant


class TestPairing(unittest.TestCase):
    def test_increment_hits(self):
        """Tests if increment_hits functions correctly.

        Calls increment_hits on 1 value, and then on 3 values.
        """
        num_participants = 5
        participant = Participant(num_participants)

        participant.increment_meetings_count(2)
        self.assertEqual(1, participant.meetings_counter[2])

        participant.increment_meetings_count(0, 1, 2)
        self.assertEqual(1, participant.meetings_counter[0])
        self.assertEqual(1, participant.meetings_counter[1])
        self.assertEqual(2, participant.meetings_counter[2])

    def test_generate_pairs(self):
        """Test to see if generate_pairs produces the correct number of
        matchings for 3 valid values for the number of participants.
        """
        num_participant_values = [4, 7, 10]
        gamma = 0
        for num_participants in num_participant_values:
            participants = [
                Participant(num_participants) for _ in range(num_participants)
            ]
            pairs = generate_pairs(participants, gamma)
            self.assertEqual(len(pairs), num_participants // 2)


if __name__ == "__main__":
    unittest.main()
