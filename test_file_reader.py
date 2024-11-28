import unittest
from file_reader import *

class TestReader(unittest.TestCase):
    def test_sync_frame_time(self):
        df = pd.read_csv(r"data\time_sync_test_eye.csv", sep = ",")
        self.assertEqual(sync_frame_time(900, df), -1)
        self.assertEqual(sync_frame_time(118, df), [5886075, 300, 200, 118])
        self.assertEqual(sync_frame_time(6, df), [5885962, 300, 200,5])

if __name__ == "__main__":
    unittest.main()