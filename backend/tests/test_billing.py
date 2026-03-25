from app.schemas.pricing import PricingEstimateRequest, PricingFormula, PricingMatchContext
from app.services.billing import BillingService


def test_pricing_formula_should_round_up_integer_credits():
    formula = PricingFormula(
        base=6,
        per_output=2,
        size_add={"l": 6},
        flag_add={"video": 8, "upscale": 3},
        model_coef={"default": 1.0, "openai:sora-2": 1.3},
        rounding="ceil_int",
    )

    credits = BillingService.calculate_credits(
        formula=formula,
        context=PricingMatchContext(
            count=2,
            size="l",
            flags=["video", "upscale"],
            model_key="openai:sora-2",
        ),
    )

    assert credits == 36


def test_pricing_estimate_should_sum_job_items():
    request = PricingEstimateRequest(
        platform="douyin",
        items=[
            {
                "category": "scene_image",
                "count": 2,
                "size": "m",
                "flags": ["upscale"],
                "model_key": "openai:gpt-image-1",
            },
            {
                "category": "video_scene",
                "count": 1,
                "size": "l",
                "flags": ["video"],
                "model_key": "openai:sora-2",
            },
        ],
    )

    result = BillingService.estimate_request(request)

    assert result.total_credits == 34
    assert len(result.items) == 2
