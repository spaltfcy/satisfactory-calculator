/*Copyright 2019 Kirk McDonald

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.*/
import { Totals } from "./totals.js"

export class Item {
    constructor(key, name, tier, img) {
        this.key = key
        this.name = name
        this.tier = tier
        this.recipes = []
        this.uses = []
        this.img = img
    }
    addRecipe(recipe) {
        this.recipes.push(recipe)
    }
    addUse(recipe) {
        this.uses.push(recipe)
    }
    produce(spec, rate, ignore) {
        let total = new Totals()
        let stack = [[this, rate, -1]]
        while (true) {
            if (!stack.length) break

            let info = stack.shift()
            let childRecipe = spec.getRecipe(info[0])
            let childRate = info[1].div(childRecipe.gives(info[0]))
            let childTotals = new Totals()

            childTotals.add(childRecipe, childRate)
            childTotals.updateHeight(childRecipe, info[2])
            total.combine(childTotals)

            if (ignore.has(childRecipe)) continue
            for (let ing of childRecipe.ingredients) 
                stack.push([ing.item, childRate.mul(ing.amount), info[2] + 1])
        }
        return total
    }
    iconPath() {
        return "images/" + this.img
    }
}

export function getItems(data) {
    let items = new Map()
    for (let d of data.items) {
        items.set(d.key_name, new Item(d.key_name, d.name, d.tier, d.image))
    }
    return items
}
