import json
import os
import os.path

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
    belt['image'] = "conveyor-belt-mk-" + id + ".png"
    belts.append(belt)
belts.sort(key=lambda x: x['name'], reverse=False)
data['belts'] = belts


# Find Recipes
# While looking for recipes also note the items and buildings we come across
recipeClass = findNativeClass("Class'/Script/FactoryGame.FGRecipe'")
discoveredBuildings = []
discoveredItems = []
recipes = []
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
            ingredients.append([ingredientName, ingredientAmount])

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
            products.append([productName, productAmount])

    # Check if a valid recipe
    if FoundIgnored or len(products) == 0:
        continue

    craftingTime = int(recipeData['mManufactoringDuration'].rstrip("0").rstrip("."))

    # Add to our recipe list
    displayName = recipeData['mDisplayName'] 
    recipe = {
        'name': displayName,
        'key_name': products[0][0],
        "category": "crafting0", #TODO pull from building tier
        'time': craftingTime,
        'ingredients': ingredients,
        'product': (products if len(products) > 1 else products[0])
    }
    if len(products) > 1:
        print("WARNING: recipe has two products: " + displayName)
    recipes.append(recipe)

    # Add to our discovered items list
    for item in ingredients:
        if item[0] not in discoveredItems:
            discoveredItems.append(item[0])
    for item in products:
        if item[0] not in discoveredItems:
            discoveredItems.append(item[0])

    # Add discovered buildings to our list
    for building in producedIn:
        if building not in discoveredBuildings:
            discoveredBuildings.append(building)

# Generate building data
buildings = []
checkBuildingClasses = [
    "Class'/Script/FactoryGame.FGBuildableManufacturerVariablePower'",
    "Class'/Script/FactoryGame.FGBuildableManufacturer'"
]
def findBuilding(name):
    for className in checkBuildingClasses:
        itemClass = findNativeClass(className)
        for itemData in itemClass:
            if itemData['ClassName'] == name:
                return itemData
for buildingName in discoveredBuildings:
    buildData = findBuilding(buildingName)
    if buildData is None:
        print("ERROR: Can't find building: " + buildingName)
        continue
    name = buildData['mDisplayName']
    key = name.lower().replace(" ", "-")
    power = int(buildData['mPowerConsumption'].rstrip("0").rstrip("."))

    building = {
        'name': name,
        'key_name': key,
        "category": "crafting0",
        "power": power,
        'image': key + ".png"
    }
    buildings.append(building)
data['buildings'] = buildings

# Hard-code for now
data['miners'] = [
    {
        "name": "Miner MK1",
        "key_name": "miner-mk1",
        "category": "mineral",
        "base_rate": 60,
        "power": 5,
        "image": "miner-mk-1.png"
    },
    {
        "name": "Miner MK2",
        "key_name": "miner-mk2",
        "category": "mineral",
        "base_rate": 120,
        "power": 12,
        "image": "miner-mk-2.png"
    },
    {
        "name": "Miner MK3",
        "key_name": "miner-mk3",
        "category": "mineral",
        "base_rate": 240,
        "power": 30,
        "image": "miner-mk-3.png"
    },
    {
        "name": "Oil Extractor",
        "key_name": "oil-extractor",
        "category": "oil",
        "base_rate": 120,
        "power": 40,
        "image": "oil-extractor.png"
    },
    {
        "name": "Water Extractor",
        "key_name": "water-extractor",
        "category": "water",
        "base_rate": 120,
        "power": 20,
        "image": "water-extractor.png"
    },
    {
        "name": "Resource Well Extractor",
        "key_name": "well-extractor",
        "category": "gas",
        "base_rate": 60,
        "power": 0,
        "image": "Unknown.png"
    }
]

#TODO auto find stack sizes?? maybe??
stackSizes = {
    'SS_ONE': 1,
    'SS_SMALL': 50,
    'SS_MEDIUM': 100,
    'SS_BIG': 100,
    'SS_HUGE': 500,
    'SS_FLUID': 60
}

# Generate item data
items = []
checkItemClasses = [
    "Class'/Script/FactoryGame.FGItemDescriptor'",
    "Class'/Script/FactoryGame.FGItemDescriptorBiomass'",
    "Class'/Script/FactoryGame.FGResourceDescriptor'",
    "Class'/Script/FactoryGame.FGEquipmentDescriptor'",
    "Class'/Script/FactoryGame.FGItemDescriptorNuclearFuel'",
    "Class'/Script/FactoryGame.FGConsumableDescriptor'"
]
def findItem(name):
    for className in checkItemClasses:
        itemClass = findNativeClass(className)
        for itemData in itemClass:
            if itemData['ClassName'] == name:
                return itemData
for itemName in discoveredItems:
    itemData = findItem(itemName)
    if itemData is None:
        print("ERROR: Can't find item: " + itemName)
        continue
    name = itemData["mDisplayName"]
    key = name.lower().replace(" ", "-")
    stackSize = 0
    stackSizeStr = itemData['mStackSize']
    if (stackSizeStr is not None) and (stackSizeStr in stackSizes):
        stackSize = stackSizes[stackSizeStr]
    item = {
        'name': name,
        'key_name': itemName,
        "tier": -1,
        "stack_size": stackSize,
        "image": key + ".png"
    }
    items.append(item)
data['items'] = items

data['recipes'] = recipes

# Hard code for now
data['resources'] = [
    {
        "key_name": "Desc_OreIron_C",
        "category": "mineral"
    },
    {
        "key_name": "Desc_OreCopper_C",
        "category": "mineral"
    },
    {
        "key_name": "Desc_Coal_C",
        "category": "mineral"
    },
    {
        "key_name": "Desc_Stone_C",
        "category": "mineral"
    },
    {
        "key_name": "Desc_OreGold_C",
        "category": "mineral"
    },
    {
        "key_name": "Desc_Sulfur_C",
        "category": "mineral"
    },
    {
        "key_name": "Desc_RawQuartz_C",
        "category": "mineral"
    },
    {
        "key_name": "Desc_LiquidOil_C",
        "category": "oil"
    },
    {
        "key_name": "Desc_OreBauxite_C",
        "category": "mineral"
    },
    {
        "key_name": "Desc_OreUranium_C",
        "category": "mineral"
    },
    {
        "key_name": "Desc_Water_C",
        "category": "water"
    },
    {
        "key_name": "Desc_NitrogenGas_C",
        "category": "gas"
    }
]

def checkImages(folder, defaultImg, dataObj, name):
    for obj in dataObj:
        if not os.path.isfile(folder + obj['image']):
            print("WARNING: Couldn't find " + name + " image: " + obj['image'])
            dataObj['image'] = defaultImg

if CheckAvailableImages:
    baseFolder = "../../images/"
    defaultImg = "Unknown.png"
    checkImages(baseFolder, defaultImg, data['belts'], "belt")
    checkImages(baseFolder, defaultImg, data['buildings'], "building")
    checkImages(baseFolder, defaultImg, data['miners'], "miner")
    checkImages(baseFolder, defaultImg, data['items'], "item")
        


#print(discoveredBuildings)
#print(discoveredItems)

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