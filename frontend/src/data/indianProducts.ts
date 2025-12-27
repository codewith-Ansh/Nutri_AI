// Fallback database for common Indian products not in OpenFoodFacts
export const indianProducts: Record<string, {name: string, ingredients: string}> = {
  // Maggi variants
  "8901030855054": {
    name: "Maggi 2-Minute Noodles Masala",
    ingredients: "Wheat flour (maida), palm oil, salt, sugar, wheat gluten, tartaric acid, guar gum, monosodium glutamate, citric acid, turmeric powder, onion powder, garlic powder, red chili powder, coriander powder, artificial flavoring substances"
  },
  "8935001704126": {
    name: "Maggi Hot & Sweet Tomato Chilli Sauce", 
    ingredients: "Water, sugar, tomato paste, vinegar, modified corn starch, salt, chili powder, garlic powder, onion powder, citric acid, sodium benzoate, potassium sorbate, artificial colors"
  },
  
  // Parle products
  "8901719101014": {
    name: "Parle-G Original Glucose Biscuits",
    ingredients: "Wheat flour, sugar, vegetable oil (palm oil), invert syrup, milk solids, leavening agents (sodium bicarbonate, ammonium bicarbonate), salt, emulsifiers, artificial vanilla flavoring"
  },
  "8901719101021": {
    name: "Parle Marie Light Biscuits", 
    ingredients: "Refined wheat flour, sugar, vegetable oil, milk solids, raising agents, salt, emulsifiers, artificial flavoring"
  },
  
  // Britannia products
  "8901063101012": {
    name: "Britannia Good Day Butter Cookies",
    ingredients: "Refined wheat flour, sugar, vegetable oil, butter, milk solids, raising agents, salt, emulsifiers, artificial butter flavoring"
  },
  "8901063101029": {
    name: "Britannia Marie Gold Biscuits",
    ingredients: "Refined wheat flour, sugar, vegetable oil, milk solids, raising agents, salt, emulsifiers"
  },
  
  // Haldiram's products  
  "8904004400014": {
    name: "Haldiram's Bhujia Sev",
    ingredients: "Gram flour, vegetable oil, moth dal flour, salt, red chili powder, black pepper powder, clove powder, asafoetida, citric acid"
  },
  "8904004400021": {
    name: "Haldiram's Aloo Bhujia",
    ingredients: "Potato flakes, gram flour, vegetable oil, salt, red chili powder, turmeric powder, coriander powder, garam masala, citric acid"
  },
  
  // Kurkure products
  "8901030801017": {
    name: "Kurkure Masala Munch",
    ingredients: "Corn meal, vegetable oil, rice meal, gram flour, salt, sugar, spices and condiments, citric acid, artificial colors, artificial flavors"
  },
  
  // Lays products
  "8901030802014": {
    name: "Lays Classic Salted Chips", 
    ingredients: "Potatoes, vegetable oil, salt"
  },
  "8901030802021": {
    name: "Lays Magic Masala Chips",
    ingredients: "Potatoes, vegetable oil, salt, sugar, spices and condiments, citric acid, artificial colors, artificial flavors"
  },
  
  // Amul products
  "8901020101011": {
    name: "Amul Full Cream Milk",
    ingredients: "Fresh cow milk, milk fat (6%), milk solids (9%)"
  },
  "8901020101028": {
    name: "Amul Butter",
    ingredients: "Fresh cream, salt"
  },
  
  // MTR products
  "8901042101015": {
    name: "MTR Ready to Eat Aloo Paratha",
    ingredients: "Wheat flour, potato, vegetable oil, salt, spices, citric acid, emulsifiers, preservatives"
  },
  
  // Bournvita
  "8901030801024": {
    name: "Cadbury Bournvita",
    ingredients: "Sugar, cocoa solids, milk solids, wheat flour, minerals, vitamins, artificial chocolate flavoring"
  },
  
  // Default fallback for unknown barcodes
  "unknown": {
    name: "Unknown Indian Product",
    ingredients: "Ingredients not available in database. Please check the package label for complete ingredient list."
  }
};