from parser import parse_movie_data

def test_parser():
    test_cases = [
        {
            "filename": "Prmovies-Subedaar_Hindi_720p.mp4",
            "caption": "Subedaar (2026) [1080p] [Hindi]",
            "expected_name": "Subedaar",
            "expected_year": "2026",
            "expected_quality": "1080p"
        },
        {
            "filename": "Filmyzilla.com-Animal_2023_Hindi_HDRip.mkv",
            "caption": None,
            "expected_name": "Animal",
            "expected_year": "2023",
            "expected_quality": "HDRip"
        },
        {
            "filename": "Khatrimaza_The_Dark_Knight_2008_720p_Dual_Audio.mp4",
            "caption": "The Dark Knight 2008 1080p Bluray",
            "expected_name": "The Dark Knight",
            "expected_year": "2008",
            "expected_quality": "1080p"
        },
        {
            "filename": "mkvking.com.Interstellar.2014.720p.Bluray.x264.mp4",
            "caption": "Interstellar (2014) [720p]",
            "expected_name": "Interstellar",
            "expected_year": "2014",
            "expected_quality": "720p"
        }
    ]

    print("--- Running Parser Tests ---")
    all_passed = True
    for i, case in enumerate(test_cases):
        text_to_parse = case["caption"] if case["caption"] else case["filename"]
        result = parse_movie_data(text_to_parse)
        
        name_match = result["movie_name"].lower() == case["expected_name"].lower()
        year_match = result["year"] == case["expected_year"]
        quality_match = result["quality"] == case["expected_quality"]
        
        if name_match and year_match and quality_match:
            print(f"Test {i+1}: PASSED")
        else:
            print(f"Test {i+1}: FAILED")
            print(f"  Input:    {text_to_parse}")
            print(f"  Actual:   Name='{result['movie_name']}', Year='{result['year']}', Quality='{result['quality']}'")
            print(f"  Expected: Name='{case['expected_name']}', Year='{case['expected_year']}', Quality='{case['expected_quality']}'")
            all_passed = False
            
    if all_passed:
        print("\nAll parser tests passed!")
    else:
        print("\nSome tests failed. Please check the logic.")

if __name__ == "__main__":
    test_parser()
