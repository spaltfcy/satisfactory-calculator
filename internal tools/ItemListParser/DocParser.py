import json

CheckAvailableImages = True
IgnoredBuildings = ["Build_Converter_C", "FGBuildGun", "BP_BuildGun_C", "BP_WorkshopComponent_C", 
    "BP_WorkBenchComponent_C", "FGBuildableAutomatedWorkBench", "Build_AutomatedWorkBench_C"
]
IgnoredItems = ["Desc_Gift_C", "Desc_XmasBranch_C", "Desc_CandyCane_C", "Desc_XmasBow_C", "Desc_Snow_C",
    "Desc_XmasBall1_C", "Desc_XmasBall3_C", "Desc_XmasBall2_C", "Desc_XmasBall4_C", "Desc_XmasBallCluster_C",
    "Desc_XmasWreath_C", "Desc_XmasStar_C", "Desc_SnowballProjectile_C", "Desc_UraniumPellet_C"
]

DocFile = open("Docs.json",)
docs = json.load(DocFile)
DocFile.close()

data = {}

imageTranslator = None
if CheckAvailableImages:
    TranslationFile = open("images.json", "r")
    imageTranslator = json.load(TranslationFile)
    TranslationFile.close()

def findNativeClass(name):
    for obj in docs:
        if obj["NativeClass"] == name:
            return obj["Classes"]

# Find conveyer belts
belts = []
conveyors = findNativeClass("Class'/Script/FactoryGame.FGBuildableConveyorBelt'") 
for conveyorData in conveyors:
    belt = {}
    belt['name'] = conveyorData["mDisplayName"]
    className = conveyorData["ClassName"]
    if((not className.endswith("_C")) or (not className[-3].isdigit())):
        continue
    id = className[-3]
    belt['key_name'] = "belt" + id
    belt['rate'] = int(conveyorData["mSpeed"].rstrip('0').rstrip('.')) // 2
    belts.append(belt)
belts.sort(key=lambda x: x['name'], reverse=False)
data['belts'] = belts


# Find Recipes
# While looking for recipes also note the items and buildings we come across
recipeClass = findNativeClass("Class'/Script/FactoryGame.FGRecipe'")
discoveredBuildings = []
discoveredItems = []
for recipeData in recipeClass:
    FoundIgnored = False
    producedInData = recipeData['mProducedIn'].lstrip("(").rstrip(")").split(",")
    producedIn = []
    for string in producedInData:
        name = string.split(".")[-1]
        if (len(name) == 0) or (name in IgnoredBuildings):
            #FoundIgnored = True
            #break
            pass
        else:
            producedIn.append(name)
    
    # Check if a valid recipe
    if FoundIgnored or len(producedIn) == 0:
        continue

    # Look for ingredients
    ingredientData = recipeData["mIngredients"].lstrip("(").rstrip(")").split(",(")
    ingredients = []
    for ingredient in ingredientData:
        ingredientName = ingredient.split(",")[0].lstrip("(").rstrip("\'").rstrip("\"").rstrip("\\").split(".")[-1]
        ingredientAmount = int(ingredient.split(",")[1].rstrip(")").split("=")[-1])

        if ingredientName in IgnoredItems:
            FoundIgnored = True
            break
        else:
            ingredients.append({'name': ingredientName, 'amount': ingredientAmount})

    # Check if a valid recipe
    if FoundIgnored or len(ingredients) == 0:
        continue

    # Find what we are producing
    productData = recipeData["mProduct"].lstrip("(").rstrip(")").split(",(")
    products = []
    for product in productData:
        productName = product.split(",")[0].lstrip("(").rstrip("\'").rstrip("\"").rstrip("\\").split(".")[-1]
        productAmount = int(product.split(",")[1].rstrip(")").split("=")[-1])
        if productName in IgnoredItems:
            FoundIgnored = True
            break
        else:
            products.append({'name': productName, 'amount': productAmount})

    # Check if a valid recipe
    if FoundIgnored or len(products) == 0:
        continue

    # Add to our discovered items list
    for item in ingredients:
        if item['name'] not in discoveredItems:
            discoveredItems.append(item['name'])
    for item in products:
        if item['name'] not in discoveredItems:
            discoveredItems.append(item['name'])

    # Add discovered buildings to our list
    for building in producedIn:
        if building not in discoveredBuildings:
            discoveredBuildings.append(building)

if CheckAvailableImages:
    pass
        
        


print(discoveredBuildings)
print(discoveredItems)
# Find buildings
#buildingsData = findNativeClass("Class'/Script/FactoryGame.FGBuildableManufacturer'")
#buildings = []
#for buildingData in buildingsData:
#    building = {}
#    building['max'] = 10 #This shouldn't effect functionality so while it is required we will just use this value
#
#data['buildings'] = buildings





# Save the data to a file
with open("data.json", 'w') as f:
    f.write(json.dumps(data, indent=4))