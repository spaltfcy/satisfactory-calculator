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
import { Rational } from "./rational.js"

class Building {
    constructor(key, name, category, power, max, img) {
        this.key = key
        this.name = name
        this.category = category
        this.power = power
        this.max = max
        this.img = img
    }
    getCount(spec, recipe, rate) {
        return rate.div(this.getRecipeRate(spec, recipe))
    }
    getRecipeRate(spec, recipe) {
        let overclock = spec.getOverclock(recipe)
        return recipe.time.reciprocate().mul(overclock)
    }
    iconPath() {
        return "images/" + this.img
    }
}

class Miner extends Building {
    constructor(key, name, category, power, baseRate, img) {
        super(key, name, category, power, null, img)
        this.baseRate = baseRate
    }
    getRecipeRate(spec, recipe) {
        let purity = spec.getResourcePurity(recipe)
        let overclock = spec.getOverclock(recipe)
        return this.baseRate.mul(purity.factor).mul(overclock)
    }
}

export function getBuildings(data) {
    let buildings = []
    for (let d of data.buildings) {
        buildings.push(new Building(
            d.key_name,
            d.name,
            d.category,
            Rational.from_float(d.power),
            d.max,
            d.image
        ))
    }
    for (let d of data.miners) {
        buildings.push(new Miner(
            d.key_name,
            d.name,
            d.category,
            Rational.from_float(d.power),
            Rational.from_float(d.base_rate).div(Rational.from_float(60)),
            d.image
        ))
    }
    return buildings
}
