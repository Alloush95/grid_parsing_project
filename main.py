# File: grid_parser_project/main.py
# Purpose: Main script to run the full pipeline

import time  # 👈 Add this
from step1_data_collection import capture_ui_screenshots
from step2_grid_parsing import process_ui_data_step2
from step3_computer_vision import process_step3
from step4_metrics_evaluation import step4_evaluation
from step5_prototype import step5_prototype_development
from step6_ai_integration import step6_ai_integration
from step7_generalization import step7_generalization_and_adaptability
from step8_final_analysis import step8_final_evaluation
from config import E_COMMERCE_WEBSITES, TEST_URLS_STEP5, BLOG_MEDIA_URLS


if __name__ == "__main__":
    start_time = time.time()  # Start tracking

    print("\n=== STEP 1: Data Collection & Annotation ===")
    capture_ui_screenshots(E_COMMERCE_WEBSITES)

    print("\n=== STEP 2: Grid-Based Parsing ===")
    process_ui_data_step2()

    print("\n=== STEP 3: Computer Vision Techniques ===")
    process_step3()

    print("\n=== STEP 4: Metric Definition & Evaluation ===")
    step4_evaluation()

    print("\n=== STEP 5: Prototype Development ===")
    step5_prototype_development(TEST_URLS_STEP5)

    # print("\n=== STEP 6: AI Integration ===")
    # step6_ai_integration(TEST_URLS_STEP5)

    print("\n=== STEP 7: Generalization & Adaptability ===")
    step7_generalization_and_adaptability(BLOG_MEDIA_URLS)

    print("\n=== STEP 8: Final Evaluation & Analysis ===")
    step8_final_evaluation()

    end_time = time.time()  # ⏱️ End tracking
    elapsed = end_time - start_time
    mins, secs = divmod(elapsed, 60)

    print(f"\n✅ All Steps (1–8) completed in {int(mins)} min {int(secs)} sec!")
