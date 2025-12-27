export interface FoodProduct {
  name: string;
  brand: string;
  category: string;
  ingredients: string[];
  nutritionPer100g?: {
    calories?: number;
    protein?: number;
    carbohydrates?: number;
    sugar?: number;
    fat?: number;
    saturatedFat?: number;
    sodium?: number;
    fiber?: number;
  };
}

export const foodProducts: FoodProduct[] = [
  {
    name: "Maggi 2-Minute Noodles",
    brand: "Nestle",
    category: "Instant Noodles",
    ingredients: [
      "Wheat flour (maida)",
      "Palm oil",
      "Salt",
      "Wheat gluten",
      "Tartaric acid (E334)",
      "Guar gum (E412)",
      "Monosodium glutamate (MSG/E621)",
      "TBHQ (Tertiary Butylhydroquinone)",
      "Hydrolyzed vegetable protein",
      "Dehydrated vegetables",
      "Spices",
      "Sugar",
      "Citric acid"
    ],
    nutritionPer100g: {
      calories: 420,
      protein: 9,
      carbohydrates: 60,
      sugar: 2,
      fat: 17,
      saturatedFat: 8,
      sodium: 820,
      fiber: 2
    }
  },
  {
    name: "Parle-G Biscuits",
    brand: "Parle",
    category: "Biscuits",
    ingredients: [
      "Wheat flour (maida)",
      "Sugar",
      "Edible vegetable oil (palm)",
      "Invert syrup",
      "Leavening agents (E500ii, E503ii)",
      "Milk solids",
      "Emulsifiers (E322, E471)",
      "Salt",
      "Dough conditioner (E223)"
    ],
    nutritionPer100g: {
      calories: 460,
      protein: 6.5,
      carbohydrates: 76,
      sugar: 26,
      fat: 14,
      saturatedFat: 7,
      sodium: 280
    }
  },
  {
    name: "Britannia Marie Gold",
    brand: "Britannia",
    category: "Biscuits",
    ingredients: [
      "Refined wheat flour (maida)",
      "Sugar",
      "Edible vegetable oil (palm)",
      "Invert syrup",
      "Milk solids",
      "Raising agents (E500ii, E503ii)",
      "Salt",
      "Emulsifiers (E322)",
      "Dough conditioner (E223)",
      "Antioxidant (E319)"
    ],
    nutritionPer100g: {
      calories: 445,
      protein: 7,
      carbohydrates: 73,
      sugar: 22,
      fat: 14,
      saturatedFat: 7,
      sodium: 320
    }
  },
  {
    name: "Amul Milk (Full Cream)",
    brand: "Amul",
    category: "Dairy",
    ingredients: [
      "Whole milk",
      "Milk solids (8.5%)",
      "Milk fat (6%)"
    ],
    nutritionPer100g: {
      calories: 67,
      protein: 3.2,
      carbohydrates: 4.7,
      sugar: 4.7,
      fat: 3.9,
      saturatedFat: 2.4,
      sodium: 50
    }
  },
  {
    name: "Haldiram's Bhujia",
    brand: "Haldiram's",
    category: "Snacks",
    ingredients: [
      "Gram flour (besan)",
      "Edible vegetable oil (palmolein)",
      "Moth dal",
      "Salt",
      "Spices",
      "Black pepper",
      "Asafoetida (hing)",
      "Antioxidant (E319)"
    ],
    nutritionPer100g: {
      calories: 560,
      protein: 18,
      carbohydrates: 45,
      fat: 35,
      saturatedFat: 16,
      sodium: 890
    }
  },
  {
    name: "MTR Ready-to-Eat Aloo Paratha",
    brand: "MTR",
    category: "Ready-to-Eat",
    ingredients: [
      "Wheat flour",
      "Potato",
      "Edible vegetable oil",
      "Salt",
      "Spices (coriander, cumin, red chilli)",
      "Citric acid (E330)",
      "Emulsifiers (E471, E472e)",
      "Acidity regulator (E500ii)"
    ],
    nutritionPer100g: {
      calories: 285,
      protein: 5,
      carbohydrates: 38,
      fat: 12,
      saturatedFat: 5,
      sodium: 420
    }
  },
  {
    name: "Tropicana Orange Juice",
    brand: "Tropicana",
    category: "Beverages",
    ingredients: [
      "Orange juice from concentrate",
      "Water",
      "Sugar",
      "Citric acid (E330)",
      "Natural orange flavoring",
      "Vitamin C (ascorbic acid)"
    ],
    nutritionPer100g: {
      calories: 45,
      protein: 0.5,
      carbohydrates: 10,
      sugar: 9,
      fat: 0,
      sodium: 5
    }
  },
  {
    name: "Kurkure Masala Munch",
    brand: "PepsiCo",
    category: "Snacks",
    ingredients: [
      "Rice meal",
      "Edible vegetable oil (palm)",
      "Corn meal",
      "Gram meal",
      "Salt",
      "Spices and condiments",
      "Sugar",
      "MSG (E621)",
      "Tartaric acid (E334)",
      "Citric acid (E330)"
    ],
    nutritionPer100g: {
      calories: 540,
      protein: 6,
      carbohydrates: 56,
      fat: 32,
      saturatedFat: 15,
      sodium: 700
    }
  },
  {
    name: "Bournvita Health Drink",
    brand: "Cadbury",
    category: "Health Drinks",
    ingredients: [
      "Sugar",
      "Malt extract",
      "Cocoa solids",
      "Milk solids",
      "Caramel (E150)",
      "Vitamins (A, B1, B2, B6, B12, C, D, E)",
      "Minerals (calcium, iron, zinc)",
      "Salt",
      "Emulsifier (E322)"
    ],
    nutritionPer100g: {
      calories: 376,
      protein: 7,
      carbohydrates: 78,
      sugar: 52,
      fat: 3,
      sodium: 180
    }
  },
  {
    name: "Good Day Butter Cookies",
    brand: "Britannia",
    category: "Biscuits",
    ingredients: [
      "Refined wheat flour (maida)",
      "Sugar",
      "Edible vegetable oil (palm)",
      "Butter (7%)",
      "Invert syrup",
      "Milk solids",
      "Raising agents (E500ii, E503ii)",
      "Salt",
      "Emulsifiers (E322, E471)",
      "Natural butter flavor"
    ],
    nutritionPer100g: {
      calories: 490,
      protein: 6,
      carbohydrates: 68,
      sugar: 28,
      fat: 20,
      saturatedFat: 10,
      sodium: 290
    }
  },
  {
    name: "Lays Classic Salted Chips",
    brand: "PepsiCo",
    category: "Snacks",
    ingredients: [
      "Potatoes",
      "Edible vegetable oil (palmolein, sunflower)",
      "Salt"
    ],
    nutritionPer100g: {
      calories: 540,
      protein: 6,
      carbohydrates: 52,
      fat: 35,
      saturatedFat: 11,
      sodium: 520
    }
  },
  {
    name: "Mother Dairy Dahi",
    brand: "Mother Dairy",
    category: "Dairy",
    ingredients: [
      "Pasteurized toned milk",
      "Live active cultures (Lactobacillus bulgaricus, Streptococcus thermophilus)"
    ],
    nutritionPer100g: {
      calories: 60,
      protein: 3.5,
      carbohydrates: 5,
      sugar: 5,
      fat: 3,
      saturatedFat: 2,
      sodium: 40
    }
  },
  {
    name: "Thums Up",
    brand: "Coca-Cola",
    category: "Beverages",
    ingredients: [
      "Carbonated water",
      "Sugar",
      "Caramel color (E150d)",
      "Phosphoric acid (E338)",
      "Natural and artificial flavoring",
      "Caffeine"
    ],
    nutritionPer100g: {
      calories: 44,
      carbohydrates: 11,
      sugar: 11,
      sodium: 10
    }
  },
  {
    name: "Frooti Mango Drink",
    brand: "Parle Agro",
    category: "Beverages",
    ingredients: [
      "Water",
      "Sugar",
      "Mango pulp (15%)",
      "Citric acid (E330)",
      "Mango flavor",
      "Preservatives (E211, E202)",
      "Antioxidant (E300)"
    ],
    nutritionPer100g: {
      calories: 55,
      carbohydrates: 13,
      sugar: 12,
      sodium: 20
    }
  },
  {
    name: "Dabur Honey",
    brand: "Dabur",
    category: "Natural Products",
    ingredients: [
      "Pure honey"
    ],
    nutritionPer100g: {
      calories: 320,
      carbohydrates: 80,
      sugar: 75,
      sodium: 5
    }
  },
  {
    name: "Kellogg's Corn Flakes",
    brand: "Kellogg's",
    category: "Breakfast Cereals",
    ingredients: [
      "Corn",
      "Sugar",
      "Malt flavoring",
      "Salt",
      "Vitamins (B1, B2, B3, B6, B12, D)",
      "Iron",
      "BHT (for freshness)"
    ],
    nutritionPer100g: {
      calories: 375,
      protein: 7,
      carbohydrates: 84,
      sugar: 8,
      fat: 0.5,
      sodium: 730,
      fiber: 3
    }
  },
  {
    name: "Kissan Mixed Fruit Jam",
    brand: "Hindustan Unilever",
    category: "Spreads",
    ingredients: [
      "Sugar",
      "Mixed fruit pulp (apple, papaya, pineapple)",
      "Pectin (E440)",
      "Citric acid (E330)",
      "Preservative (E211)",
      "Artificial colors (E110, E129)"
    ],
    nutritionPer100g: {
      calories: 270,
      carbohydrates: 67,
      sugar: 55,
      sodium: 20
    }
  },
  {
    name: "Amul Butter",
    brand: "Amul",
    category: "Dairy",
    ingredients: [
      "Pasteurized cream",
      "Salt"
    ],
    nutritionPer100g: {
      calories: 720,
      protein: 0.5,
      carbohydrates: 0.5,
      fat: 80,
      saturatedFat: 52,
      sodium: 700
    }
  },
  {
    name: "Sunfeast Dark Fantasy",
    brand: "ITC",
    category: "Biscuits",
    ingredients: [
      "Refined wheat flour (maida)",
      "Sugar",
      "Edible vegetable oil (palm)",
      "Choco chips (12%)",
      "Cocoa solids",
      "Invert syrup",
      "Raising agents (E500ii, E503ii)",
      "Milk solids",
      "Emulsifiers (E322, E471)",
      "Salt"
    ],
    nutritionPer100g: {
      calories: 505,
      protein: 5,
      carbohydrates: 62,
      sugar: 30,
      fat: 26,
      saturatedFat: 13,
      sodium: 250
    }
  },
  {
    name: "Patanjali Atta Noodles",
    brand: "Patanjali",
    category: "Instant Noodles",
    ingredients: [
      "Whole wheat flour",
      "Palm oil",
      "Salt",
      "Spices",
      "Dehydrated vegetables",
      "Onion powder",
      "Garlic powder",
      "Turmeric"
    ],
    nutritionPer100g: {
      calories: 380,
      protein: 10,
      carbohydrates: 58,
      fat: 14,
      saturatedFat: 6,
      sodium: 600,
      fiber: 4
    }
  },
  {
    name: "Real Fruit Power Mixed Fruit",
    brand: "Dabur",
    category: "Beverages",
    ingredients: [
      "Water",
      "Sugar",
      "Apple concentrate",
      "Grape concentrate",
      "Pineapple concentrate",
      "Pomegranate concentrate",
      "Citric acid (E330)",
      "Vitamin C",
      "Natural flavors"
    ],
    nutritionPer100g: {
      calories: 48,
      carbohydrates: 12,
      sugar: 11,
      sodium: 15
    }
  },
  {
    name: "Hide & Seek Chocolate Chip Cookies",
    brand: "Parle",
    category: "Biscuits",
    ingredients: [
      "Refined wheat flour (maida)",
      "Sugar",
      "Edible vegetable oil (palm)",
      "Choco chips (10%)",
      "Cocoa solids",
      "Invert syrup",
      "Raising agents (E500ii, E503ii)",
      "Emulsifiers (E322)",
      "Salt",
      "Artificial flavor"
    ],
    nutritionPer100g: {
      calories: 485,
      protein: 5.5,
      carbohydrates: 65,
      sugar: 28,
      fat: 22,
      saturatedFat: 11,
      sodium: 270
    }
  },
  {
    name: "Glucon-D Energy Drink",
    brand: "Heinz",
    category: "Health Drinks",
    ingredients: [
      "Glucose",
      "Sucrose",
      "Vitamin C",
      "Vitamin D",
      "Minerals (calcium, phosphorus)",
      "Natural orange flavor",
      "Citric acid",
      "Acidity regulator (E331)"
    ],
    nutritionPer100g: {
      calories: 400,
      carbohydrates: 99,
      sugar: 95,
      sodium: 5
    }
  },
  {
    name: "Nestle Milkmaid",
    brand: "Nestle",
    category: "Dairy",
    ingredients: [
      "Milk",
      "Sugar"
    ],
    nutritionPer100g: {
      calories: 320,
      protein: 8,
      carbohydrates: 56,
      sugar: 54,
      fat: 8,
      saturatedFat: 5,
      sodium: 120
    }
  },
  {
    name: "Saffola Gold Oil",
    brand: "Marico",
    category: "Cooking Oil",
    ingredients: [
      "Refined rice bran oil",
      "Refined sunflower oil",
      "Natural antioxidants (E306)"
    ],
    nutritionPer100g: {
      calories: 900,
      fat: 100,
      saturatedFat: 20
    }
  }
];

export const findProduct = (query: string): FoodProduct | undefined => {
  const normalizedQuery = query.toLowerCase();
  return foodProducts.find(product => 
    product.name.toLowerCase().includes(normalizedQuery) ||
    product.brand.toLowerCase().includes(normalizedQuery)
  );
};

export const searchProducts = (query: string): FoodProduct[] => {
  const normalizedQuery = query.toLowerCase();
  return foodProducts.filter(product => 
    product.name.toLowerCase().includes(normalizedQuery) ||
    product.brand.toLowerCase().includes(normalizedQuery) ||
    product.category.toLowerCase().includes(normalizedQuery)
  );
};
