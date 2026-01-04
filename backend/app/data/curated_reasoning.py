"""
Curated reasoning responses for common/demo foods.

All responses follow the canonical JSON schema:
{
  "ai_insight_title": string,
  "quick_verdict": string,
  "why_this_matters": [string, string],
  "trade_offs": {
    "positives": [string],
    "negatives": [string]
  },
  "uncertainty": string,
  "ai_advice": string
}

Health condition variants are provided where relevant.
"""

CURATED_REASONING = {
    "samosa": {
        "default": {
            "ai_insight_title": "Samosa - Deep-fried pastry with spiced filling",
            "quick_verdict": "Samosas are deep-fried pastries with refined flour wrapper and potato filling. Fine as an occasional snack but not regularly if you're health-conscious.",
            "why_this_matters": [
                "Deep-frying adds significant calories and creates trans fats that affect heart health",
                "Refined flour wrapper causes quick blood sugar spikes and provides minimal nutrition"
            ],
            "trade_offs": {
                "positives": [
                    "Provides quick energy from carbohydrates",
                    "Contains some protein and fiber from potato and spices"
                ],
                "negatives": [
                    "High in unhealthy fats from deep-frying process",
                    "Refined flour lacks nutrients and fiber",
                    "Often high in sodium which can affect blood pressure"
                ]
            },
            "uncertainty": "Oil quality and preparation methods vary significantly between vendors, which affects health impact",
            "ai_advice": "Treat samosas as an occasional indulgence rather than a regular snack. If you love them, have one mindfully and pair with vegetables."
        },
        "diabetes": {
            "ai_insight_title": "Samosa - Impact on blood sugar",
            "quick_verdict": "Samosas can spike blood sugar significantly due to refined flour wrapper and potato filling, plus deep-frying adds extra calories.",
            "why_this_matters": [
                "Refined flour (maida) in the wrapper causes rapid blood sugar spikes that are hard to manage",
                "Potato filling is high-glycemic and combined with oil creates a challenging food for diabetics"
            ],
            "trade_offs": {
                "positives": [
                    "Provides immediate energy if blood sugar is low",
                    "Spices like turmeric may have mild anti-inflammatory effects"
                ],
                "negatives": [
                    "Double carb hit from flour + potato causes significant glucose spike",
                    "Deep-frying adds calories without adding nutritional value",
                    "Difficult to estimate exact carb content for insulin dosing"
                ]
            },
            "uncertainty": "Individual blood sugar response varies based on your current control, medication timing, and activity level",
            "ai_advice": "If diabetic, limit to very occasional consumption and check blood sugar 2 hours after eating. Consider sharing one or having a small portion."
        },
        "cholesterol": {
            "ai_insight_title": "Samosa - Cholesterol impact",
            "quick_verdict": "Samosas are deep-fried which raises bad cholesterol. The oil and trans fats from frying aren't good for heart health.",
            "why_this_matters": [
                "Deep-frying creates trans fats and oxidized oils that directly increase LDL (bad cholesterol)",
                "Refined flour lacks fiber that would help remove cholesterol from your system"
            ],
            "trade_offs": {
                "positives": [
                    "Spices like cumin and coriander have minor heart-healthy properties",
                    "Can be part of balanced diet if consumed very rarely"
                ],
                "negatives": [
                    "Reused frying oil (common in street vendors) is particularly harmful",
                    "Trans fats from deep-frying lower good cholesterol while raising bad",
                    "High calorie content can lead to weight gain, worsening cholesterol"
                ]
            },
            "uncertainty": "The actual cholesterol impact depends heavily on the oil quality and whether it's been reused",
            "ai_advice": "If you have high cholesterol, it's best to avoid samosas or limit to very rare occasions. Baked versions are a better alternative."
        },
        "blood_pressure": {
            "ai_insight_title": "Samosa - Blood pressure considerations",
            "quick_verdict": "Samosas are high in sodium from the filling and deep-fried in oil, which isn't ideal for blood pressure management.",
            "why_this_matters": [
                "Sodium in the spiced filling can directly raise blood pressure by causing water retention",
                "Deep-fried foods contribute to arterial inflammation and stiffness over time"
            ],
            "trade_offs": {
                "positives": [
                    "Potatoes provide potassium which can help balance sodium",
                    "Limited portion (1 samosa) has manageable impact for most people"
                ],
                "negatives": [
                    "High sodium content from salt and spices in filling",
                    "Unhealthy fats from deep-frying affect blood vessel health",
                    "Refined carbs can indirectly affect blood pressure through weight gain"
                ]
            },
            "uncertainty": "Sodium content varies widely - homemade versions may use less salt than street vendors",
            "ai_advice": "Best avoided if you have hypertension. If you have it occasionally, skip added chutney (extra sodium) and balance with plenty of water and vegetables."
        }
    },
    "vadapav": {
        "default": {
            "ai_insight_title": "Vadapav - Mumbai street food classic",
            "quick_verdict": "Vadapav is a Mumbai street food featuring a spiced potato fritter in a bread roll. It's deep-fried and carb-heavy, so quite caloric but filling and flavorful.",
            "why_this_matters": [
                "Deep-fried potato vada adds significant calories and unhealthy fats to an already carb-rich pav (bread)",
                "Double refined carbs (fried batter + white bread) provide quick energy but little lasting nutrition"
            ],
            "trade_offs": {
                "positives": [
                    "Affordable and filling meal option",
                    "Potatoes provide some potassium and vitamin C",
                    "Spices like turmeric and garlic have health benefits"
                ],
                "negatives": [
                    "Deep-frying creates trans fats and adds empty calories",
                    "Refined flour in both vada batter and pav lacks fiber",
                    "Often served with fried chilies adding more oil"
                ]
            },
            "uncertainty": "Street vendors vary widely in oil quality and hygiene standards, which affects health impact",
            "ai_advice": "Consider vadapav an occasional treat if you're watching your diet. Sharing one or pairing with vegetables can help balance the meal."
        },
        "blood_pressure": {
            "ai_insight_title": "Vadapav - Blood pressure impact",
            "quick_verdict": "With high blood pressure, vadapav isn't ideal since it's deep-fried (high in unhealthy fats) and often contains significant salt in the potato filling.",
            "why_this_matters": [
                "Sodium in the spiced potato vada can cause water retention and raise blood pressure",
                "Deep-frying in reused oil creates oxidized fats that damage blood vessel walls over time"
            ],
            "trade_offs": {
                "positives": [
                    "Potatoes offer potassium which can help counteract sodium effects",
                    "Garlic in the chutney may have mild blood pressure lowering effects"
                ],
                "negatives": [
                    "High sodium from salt in vada and pav",
                    "Trans fats from deep-frying affect arterial health",
                    "Refined carbs contribute to weight gain which worsens hypertension"
                ]
            },
            "uncertainty": "Homemade versions with controlled salt and fresh oil are significantly healthier than street versions",
            "ai_advice": "If you want to have it occasionally, consider sharing one or having it as part of a meal with vegetables. Skip the extra chutney to reduce sodium."
        },
        "diabetes": {
            "ai_insight_title": "Vadapav - Diabetes considerations",
            "quick_verdict": "With diabetes, vadapav can spike blood sugar due to refined flour in both the pav and the fried potato vada.",
            "why_this_matters": [
                "Triple carb source (potato + batter + bread) creates a significant glucose spike",
                "Deep-fried preparation adds calories that can affect insulin resistance"
            ],
            "trade_offs": {
                "positives": [
                    "Provides quick energy if experiencing low blood sugar",
                    "Protein from gram flour in batter helps slow digestion slightly"
                ],
                "negatives": [
                    "High glycemic load from multiple refined carb sources",
                    "Oil from frying can worsen insulin sensitivity over time",
                    "Portion size is difficult to control (usually eaten whole)"
                ]
            },
            "uncertainty": "Blood sugar response varies based on your current control, medications, and activity level",
            "ai_advice": "Better as an occasional treat. If you have it, pair with protein/fiber from a side dish and monitor your blood sugar levels afterward."
        },
        "cholesterol": {
            "ai_insight_title": "Vadapav - Cholesterol impact",
            "quick_verdict": "Vadapav is deep-fried which increases bad cholesterol levels. The reused oil commonly used at street stalls is particularly harmful for heart health.",
            "why_this_matters": [
                "Deep-frying creates trans fats that raise LDL (bad) cholesterol and lower HDL (good) cholesterol",
                "Reused oil contains oxidized compounds that are especially damaging to cardiovascular health"
            ],
            "trade_offs": {
                "positives": [
                    "Garlic and turmeric in the preparation have minor cholesterol-lowering properties",
                    "Can be made healthier if air-fried or shallow-fried at home"
                ],
                "negatives": [
                    "Deep-frying in reused oil is very harmful for cholesterol",
                    "High calorie content promotes weight gain which worsens lipid profile",
                    "Lacks fiber that would help eliminate cholesterol"
                ]
            },
            "uncertainty": "Oil quality varies dramatically - fresh oil is less harmful than reused street vendor oil",
            "ai_advice": "If you have high cholesterol, it's best avoided or had very rarely. Homemade air-fried versions are a better alternative."
        }
    },
    "parle-g": {
        "default": {
            "ai_insight_title": "Parle G - Classic glucose biscuit",
            "quick_verdict": "Parle G is a popular Indian glucose biscuit made with refined flour, sugar, and oil. It's a processed snack that gives quick energy but isn't very nutritious.",
            "why_this_matters": [
                "Contains refined flour (maida) and added sugar which provide quick energy but no sustained nutrition",
                "Processing removes most natural nutrients; primarily provides empty calories"
            ],
            "trade_offs": {
                "positives": [
                    "Affordable and convenient quick energy source",
                    "Long shelf life makes it practical for storage",
                    "Familiar comfort food that pairs well with tea"
                ],
                "negatives": [
                    "High in refined carbs and added sugar",
                    "Contains palm oil which is high in saturated fat",
                    "Low in protein, fiber, and essential nutrients"
                ]
            },
            "uncertainty": "Individual portions vary - eating 1-2 biscuits has different impact than consuming a whole packet",
            "ai_advice": "Fine as an occasional treat with tea, but not as a regular snack. Better options exist for daily nutrition."
        },
        "diabetes": {
            "ai_insight_title": "Parle G - Diabetes impact",
            "quick_verdict": "With diabetes, Parle G can cause blood sugar spikes since it contains refined flour (maida) and added sugar.",
            "why_this_matters": [
                "Refined flour breaks down quickly into glucose, causing rapid blood sugar elevation",
                "Added sugar compounds the glycemic impact, making it challenging for blood sugar control"
            ],
            "trade_offs": {
                "positives": [
                    "Useful for treating low blood sugar episodes (hypoglycemia)",
                    "Portion-controlled - easier to count carbs than many snacks"
                ],
                "negatives": [
                    "High glycemic index causes sharp blood sugar spikes",
                    "Lacks protein or fiber to slow glucose absorption",
                    "Easy to overeat due to small size and taste"
                ]
            },
            "uncertainty": "Blood sugar response depends on how many you eat, whether you have them with a meal, and your current glucose control",
            "ai_advice": "If you want to have it, try limiting to 1-2 biscuits with a meal rather than alone, and monitor your blood sugar. Better to discuss portion sizes with your doctor."
        }
    },
    "bhel-puri": {
        "default": {
            "ai_insight_title": "Bhel Puri - Street chaat snack",
            "quick_verdict": "Bhel puri is a popular street snack with puffed rice, vegetables, chutneys, and spices. It's relatively light but can be high in sodium and depends heavily on vendor hygiene.",
            "why_this_matters": [
                "Sodium from chutneys and sev can be significant, especially from street vendors who may use excess salt",
                "Hygiene standards vary widely; contamination risk from raw vegetables and water-based chutneys"
            ],
            "trade_offs": {
                "positives": [
                    "Lower in calories than fried snacks due to puffed rice base",
                    "Contains vegetables like onions, tomatoes providing some vitamins",
                    "Tangy tamarind has antioxidants and aids digestion"
                ],
                "negatives": [
                    "High sodium content from chutneys and salt",
                    "Food safety concerns with street vendors",
                    "Sev (fried noodles) adds unhealthy fats"
                ]
            },
            "uncertainty": "Quality and safety vary dramatically between vendors - clean, reputable vendors are much safer",
            "ai_advice": "Enjoy occasionally from clean vendors you trust. Homemade versions let you control salt and ensure hygiene."
        }
    },
    "dosa": {
        "default": {
            "ai_insight_title": "Dosa - Fermented rice and lentil crepe",
            "quick_verdict": "Dosa is a fermented crepe made from rice and lentils. It's relatively healthy, especially plain dosa, and the fermentation adds beneficial probiotics.",
            "why_this_matters": [
                "Fermentation process creates probiotics that support gut health and improves nutrient absorption",
                "Lentils add protein and make it more balanced than pure rice dishes"
            ],
            "trade_offs": {
                "positives": [
                    "Fermentation makes nutrients more bioavailable and easier to digest",
                    "Combination of rice and lentils provides complete protein",
                    "Plain dosa uses minimal oil compared to other fried foods"
                ],
                "negatives": [
                    "White rice base can still spike blood sugar for some people",
                    "Masala dosa filling (potato) adds refined carbs",
                    "Often served with coconut chutney which is high in saturated fat"
                ]
            },
            "uncertainty": "Oil quantity varies by preparation - restaurant dosas often use more oil than traditional homemade",
            "ai_advice": "Plain dosa with sambar is a good choice. Avoid heavy potato masala filling and go easy on coconut chutney."
        },
        "diabetes": {
            "ai_insight_title": "Dosa - Diabetes considerations",
            "quick_verdict": "Plain dosa is better for diabetes than many options since it's fermented and has some protein from lentils, but avoid potato masala filling.",
            "why_this_matters": [
                "Fermentation lowers the glycemic index compared to unfermented rice products",
                "Protein from urad dal helps slow down glucose absorption"
            ],
            "trade_offs": {
                "positives": [
                    "Lower glycemic index due to fermentation process",
                    "Protein content helps stabilize blood sugar response",
                    "Pairing with sambar adds fiber and protein"
                ],
                "negatives": [
                    "Still primarily a carbohydrate source that will raise blood sugar",
                    "Masala filling is high-glycemic potato",
                    "Restaurant portions can be large"
                ]
            },
            "uncertainty": "Individual blood sugar response varies - some diabetics tolerate dosa well, others may see significant spikes",
            "ai_advice": "Choose plain dosa over masala, pair with protein-rich sambar, and monitor portions. Skip coconut chutney to avoid extra calories."
        }
    },
    "maggi": {
        "default": {
            "ai_insight_title": "Maggi - Instant noodles",
            "quick_verdict": "Maggi and instant noodles are processed foods high in sodium, preservatives, and refined carbs. They're convenient but not nutritious.",
            "why_this_matters": [
                "Very high sodium content (one serving can exceed half your daily limit) affects blood pressure and kidney health",
                "Ultra-processed with preservatives and additives that may have long-term health effects"
            ],
            "trade_offs": {
                "positives": [
                    "Quick and convenient meal solution",
                    "Long shelf life for emergency food storage",
                    "Can be upgraded with added vegetables and protein"
                ],
                "negatives": [
                    "Extremely high in sodium (>900mg per serving)",
                    "Contains preservatives like TBHQ",
                    "Refined wheat provides little nutritional value",
                    "Low in protein, fiber, and essential nutrients"
                ]
            },
            "uncertainty": "Health impact increases with frequency - occasional consumption is less concerning than regular meals",
            "ai_advice": "Better as an occasional quick meal than a regular option. If you must have it, use less masala packet and add vegetables to improve nutrition."
        }
    }
}

# Health condition detection patterns
HEALTH_CONDITIONS = {
    'diabetes': ['diabetes', 'diabetic', 'blood sugar', 'sugar level', 'glucose'],
    'blood_pressure': ['blood pressure', 'hypertension', 'bp', 'high bp'],
    'cholesterol': ['cholesterol', 'high cholesterol', 'ldl', 'hdl'],
    'heart': ['heart disease', 'heart problem', 'cardiac'],
    'weight': ['weight loss', 'obesity', 'overweight', 'fat loss']
}

# Food name variations/aliases
FOOD_ALIASES = {
    'vada pav': 'vadapav',
    'vada-pav': 'vadapav',
    'wada pav': 'vadapav',
    'parle g': 'parle-g',
    'parleg': 'parle-g',
    'parle-g biscuit': 'parle-g',
    'bhelpuri': 'bhel-puri',
    'bhel': 'bhel-puri',
}


def get_curated_response(user_input: str) -> dict:
    """
    Get curated response for known foods.
    
    Args:
        user_input: The user's message text
        
    Returns:
        Structured JSON response dict if match found, None otherwise
    """
    user_lower = user_input.lower().strip()
    
    # Detect food item
    detected_food = None
    for food_key in CURATED_REASONING.keys():
        if food_key in user_lower:
            detected_food = food_key
            break
    
    # Check aliases
    if not detected_food:
        for alias, canonical in FOOD_ALIASES.items():
            if alias in user_lower:
                detected_food = canonical
                break
    
    if not detected_food:
        return None
    
    # Detect health condition
    detected_condition = None
    for condition, terms in HEALTH_CONDITIONS.items():
        if any(term in user_lower for term in terms):
            detected_condition = condition
            break
    
    # Get appropriate response
    food_responses = CURATED_REASONING.get(detected_food, {})
    
    if detected_condition and detected_condition in food_responses:
        response = food_responses[detected_condition].copy()
    else:
        response = food_responses.get('default', {}).copy()
    
    # Add metadata
    response['_source'] = 'curated'
    response['_food'] = detected_food
    if detected_condition:
        response['_condition'] = detected_condition
    
    return response if response else None
