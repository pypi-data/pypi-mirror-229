import os
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _card_component = components.declare_component(
        "card_component",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _card_component = components.declare_component("card_component", path=build_dir)

def card_component(data=None, styles=None, typeExpand=None, showAdd=None, addHeroComponent=None, showHero=None, showChartSwitch=None, saveEdits=None, EditDashboard=None, userSetRating=None, key=None):
    
    # if on_change is not None:
    #     if key is None:
    #         st.error("You must pass a key if you want to use the on_change callback for the option menu")
    #     else:    
    #         register_callback(key, on_change, key)
  
    component_value = _card_component(
        data=data, 
        styles=styles, 
        typeExpand=typeExpand, 
        showAdd=showAdd, 
        addHeroComponent=addHeroComponent, 
        showHero=showHero, 
        showChartSwitch=showChartSwitch, 
        saveEdits=saveEdits,
        EditDashboard=EditDashboard,
        userSetRating=userSetRating,
        key=key, 
        default=0
        )

    return component_value

if not _RELEASE:
    import streamlit as st


    st.set_page_config(layout="wide")

    data = [
        {
      "index": 0,
      "addNewHero":False,
      "toStore":False,
      "hasChanged":False,
      "remove":False,
      "confirmRemove":False,
      "clickedChange":False,
      "ratings":0,
      "numOfUsersRatedVal": 80,
      "indexName": "equipmentItems",
      "title": "Equipment name",
      "titleVal":"equipment name",
      "numOfHeroes": [
        {
          "index": 0,
          "sum": "+7",
          "expand": True,
         "heroesUserAttachedToSet": [ ]
        }
      ],
      "changeTitleBtnLayout":{"disabled":True},
      "changeTitleTxtF":{"value":"", "autoFocus":True},
      "chipLayout":{"size":"small"},
      "expand": False,
      "heroData": [
          {
              "index": 0,
              "name": "Beatrix",
              "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 1,
              "name": "Brody",
              "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 2,
              "name": "Bruno",
              "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 3,
              "name": "Claude",
              "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 4,
              "name": "Clint",
              "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 5,
              "name": "Granger",
              "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
  
            {
              "index": 6,
              "name": "Beatrix",
              "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 7,
              "name": "Brody",
              "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 8,
              "name": "Bruno",
              "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 9,
              "name": "Claude",
              "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 10,
              "name": "Clint",
              "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 11,
              "name": "Granger",
              "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
      ],
      "equippmentList": [
        {
          "index": 0,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 1,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 2,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 3,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 4,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 5,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        }
      ],
      "equipmentCategory": [
        { "index": 0, "name": "Attack", "color": "#880808" },
        { "index": 1, "name": "Magic", "color": "#0047AB" },
        { "index": 2, "name": "Defense", "color": "#50C878" }
        # { "index": 3, "name": "Movement", "color": "#C19A6B" },
        # { "index": 4, "name": "Jungling", "color": "#702963" },
        # { "index": 5, "name": "Roaming", "color": "#40B5AD" }
      ],
      "top3Equipment": [
        { "index": 0, "name": "Health", "stat": "+4453" },
        { "index": 1, "name": "Magic Power", "stat": "+589" },
        { "index": 2, "name": "Atk Speed", "stat": "+33%" }
      ],
      "bottom3Equipment": [
        { "index": 0, "name": "Health", "stat": "+4453" },
        { "index": 1, "name": "Magic Power", "stat": "+589" },
        { "index": 2, "name": "Atk Speed", "stat": "+33%" }
      ],
      "expandData": [
        {
          "index": 0,
          "tabTitle": "Visualize",
          "toggle": False,
          "vizualizeD": [
            {
              "index": 0,
              "equipCatChecked": False,
              "dataToDisplayOriginal": [
                {
                  "skillFeature": "Attack_Speed",
                  "total": 190,
                  "attack": 20,
                  "magic": 30,
                  "defense": 30,
                  "movement": 70,
                  "jungling": 15,
                  "roaming": 15
                },
                {
                  "skillFeature": "CD_Reduction",
                  "total": 100,
                  "attack": 20,
                  "magic": 30,
                  "defense": 10,
                  "movement": 10,
                  "jungling": 15,
                  "roaming": 15
                },
                {
                  "skillFeature": "Crit_Chance",
                  "total": 50,
                  "attack": 20,
                  "magic": 5,
                  "defense": 5,
                  "movement": 5,
                  "jungling": 5,
                  "roaming": 10
                }
              ],
              "keysOrigin": [
                "total",
                "attack",
                "magic",
                "defense",
                "movement",
                "jungling",
                "roaming"
              ],
              "dataToDisplayCat": [
                {
                  "skillFeature": "Attack_Speed",
                  "total": 190,
                  "attack": 20,
                  "magic": 30,
                  "defense": 30,
                  "movement": 70,
                  "jungling": 15,
                  "roaming": 15
                },
                {
                  "skillFeature": "CD_Reduction",
                  "total": 100,
                  "attack": 20,
                  "magic": 30,
                  "defense": 10,
                  "movement": 10,
                  "jungling": 15,
                  "roaming": 15
                },
                {
                  "skillFeature": "Crit_Chance",
                  "total": 50,
                  "attack": 20,
                  "magic": 5,
                  "defense": 5,
                  "movement": 5,
                  "jungling": 5,
                  "roaming": 10
                }
              ],
              "chartLayout": {
                "keys": ["total"],
                "indexBy": "skillFeature",
                "margin": { "right": 85, "bottom": 40, "left": 30, "top": 20 },
                "labelSkipHeight": 12,
                "legends": [
                  {
                    "dataFrom": "keys",
                    "anchor": "bottom-right",
                    "direction": "column",
                    "justify": False,
                    "translateX": 100,
                    "translateY": 0,
                    "itemsSpacing": 2,
                    "itemWidth": 100,
                    "itemHeight": 20,
                    "itemDirection": "left-to-right",
                    "itemOpacity": 0.85,
                    "symbolSize": 20,
                    "effects": [
                      {
                        "on": "hover",
                        "style": {
                          "itemOpacity": 1
                        }
                      }
                    ]
                  }
                ]
              }
            }
          ],
          "gridD": [
            { "index": 0, "name": "Attack_Speed", "stat": "34%" },
            { "index": 1, "name": "CD_Reduction", "stat": "8%" },
            { "index": 2, "name": "Crit_Chance", "stat": "14%" },
            { "index": 3, "name": "HP", "stat": "4560" },
            { "index": 4, "name": "HP_Regen", "stat": "8" },
            { "index": 5, "name": "Hybrid_Lifesteal", "stat": "8" },
            { "index": 6, "name": "Lifesteal", "stat": "12" },
            { "index": 7, "name": "Magic_Defense", "stat": "115" },
            { "index": 8, "name": "Magic_Lifesteal", "stat": "7" },
            { "index": 9, "name": "Magic_PEN", "stat": "25%" },
            { "index": 10, "name": "Magic_Power", "stat": "308" },
            { "index": 11, "name": "Mana", "stat": "100" },
            { "index": 12, "name": "Mana_Regen", "stat": "8" },
            { "index": 13, "name": "Movement_Speed", "stat": "70" },
            { "index": 14, "name": "Physical_Attack", "stat": "689" },
            { "index": 15, "name": "Physical_Defense", "stat": "350" },
            { "index": 16, "name": "Spell_Vamp", "stat": "8" }
          ]
        }
      ]
    },
        {
        "index": 1,
        "addNewHero":False,
        "toStore":False,
         "hasChanged":False,
        "remove":False,
      "confirmRemove":False,
      "clickedChange":False,
      "ratings":0,
      "numOfUsersRatedVal": 80,
        "indexName": "equipmentItems",
        "title": "Equipment name",
        "titleVal":"equipment name",
        "numOfHeroes": [
            {
            "index": 0,
            "sum": "+7",
            "expand": True,
            "heroesUserAttachedToSet": [ ]
            }
        ],
        "changeTitleBtnLayout":{"disabled":True},
        "changeTitleTxtF":{"value":"", "autoFocus":True},
        "chipLayout":{"size":"small"},
        "expand": False,
        "heroData": [
            {
                "index": 0,
                "name": "Beatrix",
                "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 1,
                "name": "Brody",
                "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 2,
                "name": "Bruno",
                "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 3,
                "name": "Claude",
                "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 4,
                "name": "Clint",
                "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 5,
                "name": "Granger",
                "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
    
                {
                "index": 6,
                "name": "Beatrix",
                "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 7,
                "name": "Brody",
                "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 8,
                "name": "Bruno",
                "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 9,
                "name": "Claude",
                "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 10,
                "name": "Clint",
                "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 11,
                "name": "Granger",
                "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
        ],
        "equippmentList": [
            {
            "index": 0,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 1,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 2,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 3,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 4,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 5,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            }
        ],
        "equipmentCategory": [
            { "index": 0, "name": "Attack", "color": "#880808" },
            { "index": 1, "name": "Magic", "color": "#0047AB" },
            { "index": 2, "name": "Defense", "color": "#50C878" }
            # { "index": 3, "name": "Movement", "color": "#C19A6B" },
            # { "index": 4, "name": "Jungling", "color": "#702963" },
            # { "index": 5, "name": "Roaming", "color": "#40B5AD" }
        ],
        "top3Equipment": [
            { "index": 0, "name": "Health", "stat": "+4453" },
            { "index": 1, "name": "Magic Power", "stat": "+589" },
            { "index": 2, "name": "Atk Speed", "stat": "+33%" }
        ],
        "bottom3Equipment": [
            { "index": 0, "name": "Health", "stat": "+4453" },
            { "index": 1, "name": "Magic Power", "stat": "+589" },
            { "index": 2, "name": "Atk Speed", "stat": "+33%" }
        ],
        "expandData": [
            {
            "index": 0,
            "tabTitle": "Visualize",
            "toggle": False,
            "vizualizeD": [
                {
                "index": 0,
                "equipCatChecked": False,
                "dataToDisplayOriginal": [
                    {
                    "skillFeature": "Attack_Speed",
                    "total": 190,
                    "attack": 20,
                    "magic": 30,
                    "defense": 30,
                    "movement": 70,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "CD_Reduction",
                    "total": 100,
                    "attack": 20,
                    "magic": 30,
                    "defense": 10,
                    "movement": 10,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "Crit_Chance",
                    "total": 50,
                    "attack": 20,
                    "magic": 5,
                    "defense": 5,
                    "movement": 5,
                    "jungling": 5,
                    "roaming": 10
                    }
                ],
                "keysOrigin": [
                    "total",
                    "attack",
                    "magic",
                    "defense",
                    "movement",
                    "jungling",
                    "roaming"
                ],
                "dataToDisplayCat": [
                    {
                    "skillFeature": "Attack_Speed",
                    "total": 190,
                    "attack": 20,
                    "magic": 30,
                    "defense": 30,
                    "movement": 70,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "CD_Reduction",
                    "total": 100,
                    "attack": 20,
                    "magic": 30,
                    "defense": 10,
                    "movement": 10,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "Crit_Chance",
                    "total": 50,
                    "attack": 20,
                    "magic": 5,
                    "defense": 5,
                    "movement": 5,
                    "jungling": 5,
                    "roaming": 10
                    }
                ],
                "chartLayout": {
                    "keys": ["total"],
                    "indexBy": "skillFeature",
                    "margin": { "right": 85, "bottom": 40, "left": 30, "top": 20 },
                    "labelSkipHeight": 12,
                    "legends": [
                    {
                        "dataFrom": "keys",
                        "anchor": "bottom-right",
                        "direction": "column",
                        "justify": False,
                        "translateX": 100,
                        "translateY": 0,
                        "itemsSpacing": 2,
                        "itemWidth": 100,
                        "itemHeight": 20,
                        "itemDirection": "left-to-right",
                        "itemOpacity": 0.85,
                        "symbolSize": 20,
                        "effects": [
                        {
                            "on": "hover",
                            "style": {
                            "itemOpacity": 1
                            }
                        }
                        ]
                    }
                    ]
                }
                }
            ],
            "gridD": [
                { "index": 0, "name": "Attack_Speed", "stat": "34%" },
                { "index": 1, "name": "CD_Reduction", "stat": "8%" },
                { "index": 2, "name": "Crit_Chance", "stat": "14%" },
                { "index": 3, "name": "HP", "stat": "4560" },
                { "index": 4, "name": "HP_Regen", "stat": "8" },
                { "index": 5, "name": "Hybrid_Lifesteal", "stat": "8" },
                { "index": 6, "name": "Lifesteal", "stat": "12" },
                { "index": 7, "name": "Magic_Defense", "stat": "115" },
                { "index": 8, "name": "Magic_Lifesteal", "stat": "7" },
                { "index": 9, "name": "Magic_PEN", "stat": "25%" },
                { "index": 10, "name": "Magic_Power", "stat": "308" },
                { "index": 11, "name": "Mana", "stat": "100" },
                { "index": 12, "name": "Mana_Regen", "stat": "8" },
                { "index": 13, "name": "Movement_Speed", "stat": "70" },
                { "index": 14, "name": "Physical_Attack", "stat": "689" },
                { "index": 15, "name": "Physical_Defense", "stat": "350" },
                { "index": 16, "name": "Spell_Vamp", "stat": "8" }
            ]
            }
        ]
        },
        {
        "index": 2,
        "addNewHero":False,
        "toStore":False,
         "hasChanged":False,
        "remove":False,
      "confirmRemove":False,
      "clickedChange":False,
        "ratings":0,
        "numOfUsersRatedVal": 80,
        "indexName": "equipmentItems",
        "title": "Equipment name",
        "titleVal":"equipment name",
        "numOfHeroes": [
            {
            "index": 0,
            "sum": "+7",
            "expand": True,
            "heroesUserAttachedToSet": [ ]
            }
        ],
        "changeTitleBtnLayout":{"disabled":True},
        "changeTitleTxtF":{"value":"", "autoFocus":True},
        "chipLayout":{"size":"small"},
        "expand": False,
        "heroData": [
            {
                "index": 0,
                "name": "Beatrix",
                "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 1,
                "name": "Brody",
                "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 2,
                "name": "Bruno",
                "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 3,
                "name": "Claude",
                "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 4,
                "name": "Clint",
                "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 5,
                "name": "Granger",
                "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
    
                {
                "index": 6,
                "name": "Beatrix",
                "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 7,
                "name": "Brody",
                "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 8,
                "name": "Bruno",
                "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 9,
                "name": "Claude",
                "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 10,
                "name": "Clint",
                "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 11,
                "name": "Granger",
                "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
        ],
        "equippmentList": [
            {
            "index": 0,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 1,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 2,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 3,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 4,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 5,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            }
        ],
        "equipmentCategory": [
            { "index": 0, "name": "Attack", "color": "#880808" },
            { "index": 1, "name": "Magic", "color": "#0047AB" },
            { "index": 2, "name": "Defense", "color": "#50C878" }
            # { "index": 3, "name": "Movement", "color": "#C19A6B" },
            # { "index": 4, "name": "Jungling", "color": "#702963" },
            # { "index": 5, "name": "Roaming", "color": "#40B5AD" }
        ],
        "top3Equipment": [
            { "index": 0, "name": "Health", "stat": "+4453" },
            { "index": 1, "name": "Magic Power", "stat": "+589" },
            { "index": 2, "name": "Atk Speed", "stat": "+33%" }
        ],
        "bottom3Equipment": [
            { "index": 0, "name": "Health", "stat": "+4453" },
            { "index": 1, "name": "Magic Power", "stat": "+589" },
            { "index": 2, "name": "Atk Speed", "stat": "+33%" }
        ],
        "expandData": [
            {
            "index": 0,
            "tabTitle": "Visualize",
            "toggle": False,
            "vizualizeD": [
                {
                "index": 0,
                "equipCatChecked": False,
                "dataToDisplayOriginal": [
                    {
                    "skillFeature": "Attack_Speed",
                    "total": 190,
                    "attack": 20,
                    "magic": 30,
                    "defense": 30,
                    "movement": 70,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "CD_Reduction",
                    "total": 100,
                    "attack": 20,
                    "magic": 30,
                    "defense": 10,
                    "movement": 10,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "Crit_Chance",
                    "total": 50,
                    "attack": 20,
                    "magic": 5,
                    "defense": 5,
                    "movement": 5,
                    "jungling": 5,
                    "roaming": 10
                    }
                ],
                "keysOrigin": [
                    "total",
                    "attack",
                    "magic",
                    "defense",
                    "movement",
                    "jungling",
                    "roaming"
                ],
                "dataToDisplayCat": [
                    {
                    "skillFeature": "Attack_Speed",
                    "total": 190,
                    "attack": 20,
                    "magic": 30,
                    "defense": 30,
                    "movement": 70,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "CD_Reduction",
                    "total": 100,
                    "attack": 20,
                    "magic": 30,
                    "defense": 10,
                    "movement": 10,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "Crit_Chance",
                    "total": 50,
                    "attack": 20,
                    "magic": 5,
                    "defense": 5,
                    "movement": 5,
                    "jungling": 5,
                    "roaming": 10
                    }
                ],
                "chartLayout": {
                    "keys": ["total"],
                    "indexBy": "skillFeature",
                    "margin": { "right": 85, "bottom": 40, "left": 30, "top": 20 },
                    "labelSkipHeight": 12,
                    "legends": [
                    {
                        "dataFrom": "keys",
                        "anchor": "bottom-right",
                        "direction": "column",
                        "justify": False,
                        "translateX": 100,
                        "translateY": 0,
                        "itemsSpacing": 2,
                        "itemWidth": 100,
                        "itemHeight": 20,
                        "itemDirection": "left-to-right",
                        "itemOpacity": 0.85,
                        "symbolSize": 20,
                        "effects": [
                        {
                            "on": "hover",
                            "style": {
                            "itemOpacity": 1
                            }
                        }
                        ]
                    }
                    ]
                }
                }
            ],
            "gridD": [
                { "index": 0, "name": "Attack_Speed", "stat": "34%" },
                { "index": 1, "name": "CD_Reduction", "stat": "8%" },
                { "index": 2, "name": "Crit_Chance", "stat": "14%" },
                { "index": 3, "name": "HP", "stat": "4560" },
                { "index": 4, "name": "HP_Regen", "stat": "8" },
                { "index": 5, "name": "Hybrid_Lifesteal", "stat": "8" },
                { "index": 6, "name": "Lifesteal", "stat": "12" },
                { "index": 7, "name": "Magic_Defense", "stat": "115" },
                { "index": 8, "name": "Magic_Lifesteal", "stat": "7" },
                { "index": 9, "name": "Magic_PEN", "stat": "25%" },
                { "index": 10, "name": "Magic_Power", "stat": "308" },
                { "index": 11, "name": "Mana", "stat": "100" },
                { "index": 12, "name": "Mana_Regen", "stat": "8" },
                { "index": 13, "name": "Movement_Speed", "stat": "70" },
                { "index": 14, "name": "Physical_Attack", "stat": "689" },
                { "index": 15, "name": "Physical_Defense", "stat": "350" },
                { "index": 16, "name": "Spell_Vamp", "stat": "8" }
            ]
            }
        ]
        },
        {
        "index": 3,
        "addNewHero":False,
        "toStore":False,
         "hasChanged":False,
        "remove":False,
      "confirmRemove":False,
      "clickedChange":False,
        "ratings":0,
        "numOfUsersRatedVal": 80,
        "indexName": "equipmentItems",
        "title": "Equipment name",
        "numOfHeroes": [
            {
            "index": 0,
            "sum": "+7",
            "expand": True,
            "heroesUserAttachedToSet": [ ]
            }
        ],
        "changeTitleBtnLayout":{"disabled":True},
        "changeTitleTxtF":{"value":"", "autoFocus":True},
        "chipLayout":{"size":"small"},
        "expand": False,
        "heroData": [
            {
                "index": 0,
                "name": "Beatrix",
                "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 1,
                "name": "Brody",
                "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 2,
                "name": "Bruno",
                "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 3,
                "name": "Claude",
                "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 4,
                "name": "Clint",
                "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 5,
                "name": "Granger",
                "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
    
                {
                "index": 6,
                "name": "Beatrix",
                "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 7,
                "name": "Brody",
                "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 8,
                "name": "Bruno",
                "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 9,
                "name": "Claude",
                "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 10,
                "name": "Clint",
                "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
                {
                "index": 11,
                "name": "Granger",
                "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
                "clicked":False, "Layout":{"color":"default"}
                },
        ],
        "equippmentList": [
            {
            "index": 0,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 1,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 2,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 3,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 4,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            },
            {
            "index": 5,
            "name": "Tough Boots",
            "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
            }
        ],
        "equipmentCategory": [
            { "index": 0, "name": "Attack", "color": "#880808" },
            { "index": 1, "name": "Magic", "color": "#0047AB" },
            { "index": 2, "name": "Defense", "color": "#50C878" }
            # { "index": 3, "name": "Movement", "color": "#C19A6B" },
            # { "index": 4, "name": "Jungling", "color": "#702963" },
            # { "index": 5, "name": "Roaming", "color": "#40B5AD" }
        ],
        "top3Equipment": [
            { "index": 0, "name": "Health", "stat": "+4453" },
            { "index": 1, "name": "Magic Power", "stat": "+589" },
            { "index": 2, "name": "Atk Speed", "stat": "+33%" }
        ],
        "bottom3Equipment": [
            { "index": 0, "name": "Health", "stat": "+4453" },
            { "index": 1, "name": "Magic Power", "stat": "+589" },
            { "index": 2, "name": "Atk Speed", "stat": "+33%" }
        ],
        "expandData": [
            {
            "index": 0,
            "tabTitle": "Visualize",
            "toggle": False,
            "vizualizeD": [
                {
                "index": 0,
                "equipCatChecked": False,
                "dataToDisplayOriginal": [
                    {
                    "skillFeature": "Attack_Speed",
                    "total": 190,
                    "attack": 20,
                    "magic": 30,
                    "defense": 30,
                    "movement": 70,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "CD_Reduction",
                    "total": 100,
                    "attack": 20,
                    "magic": 30,
                    "defense": 10,
                    "movement": 10,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "Crit_Chance",
                    "total": 50,
                    "attack": 20,
                    "magic": 5,
                    "defense": 5,
                    "movement": 5,
                    "jungling": 5,
                    "roaming": 10
                    }
                ],
                "keysOrigin": [
                    "total",
                    "attack",
                    "magic",
                    "defense",
                    "movement",
                    "jungling",
                    "roaming"
                ],
                "dataToDisplayCat": [
                    {
                    "skillFeature": "Attack_Speed",
                    "total": 190,
                    "attack": 20,
                    "magic": 30,
                    "defense": 30,
                    "movement": 70,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "CD_Reduction",
                    "total": 100,
                    "attack": 20,
                    "magic": 30,
                    "defense": 10,
                    "movement": 10,
                    "jungling": 15,
                    "roaming": 15
                    },
                    {
                    "skillFeature": "Crit_Chance",
                    "total": 50,
                    "attack": 20,
                    "magic": 5,
                    "defense": 5,
                    "movement": 5,
                    "jungling": 5,
                    "roaming": 10
                    }
                ],
                "chartLayout": {
                    "keys": ["total"],
                    "indexBy": "skillFeature",
                    "margin": { "right": 85, "bottom": 40, "left": 30, "top": 20 },
                    "labelSkipHeight": 12,
                    "legends": [
                    {
                        "dataFrom": "keys",
                        "anchor": "bottom-right",
                        "direction": "column",
                        "justify": False,
                        "translateX": 100,
                        "translateY": 0,
                        "itemsSpacing": 2,
                        "itemWidth": 100,
                        "itemHeight": 20,
                        "itemDirection": "left-to-right",
                        "itemOpacity": 0.85,
                        "symbolSize": 20,
                        "effects": [
                        {
                            "on": "hover",
                            "style": {
                            "itemOpacity": 1
                            }
                        }
                        ]
                    }
                    ]
                }
                }
            ],
            "gridD": [
                { "index": 0, "name": "Attack_Speed", "stat": "34%" },
                { "index": 1, "name": "CD_Reduction", "stat": "8%" },
                { "index": 2, "name": "Crit_Chance", "stat": "14%" },
                { "index": 3, "name": "HP", "stat": "4560" },
                { "index": 4, "name": "HP_Regen", "stat": "8" },
                { "index": 5, "name": "Hybrid_Lifesteal", "stat": "8" },
                { "index": 6, "name": "Lifesteal", "stat": "12" },
                { "index": 7, "name": "Magic_Defense", "stat": "115" },
                { "index": 8, "name": "Magic_Lifesteal", "stat": "7" },
                { "index": 9, "name": "Magic_PEN", "stat": "25%" },
                { "index": 10, "name": "Magic_Power", "stat": "308" },
                { "index": 11, "name": "Mana", "stat": "100" },
                { "index": 12, "name": "Mana_Regen", "stat": "8" },
                { "index": 13, "name": "Movement_Speed", "stat": "70" },
                { "index": 14, "name": "Physical_Attack", "stat": "689" },
                { "index": 15, "name": "Physical_Defense", "stat": "350" },
                { "index": 16, "name": "Spell_Vamp", "stat": "8" }
            ]
            }
        ]
        },
        {
      "index": 4,
      "addNewHero":False,
      "toStore":False,
       "hasChanged":False,
      "remove":False,
      "confirmRemove":False,
      "clickedChange":False,
     "ratings":0,
     "numOfUsersRatedVal": 80,
      "indexName": "equipmentItems",
      "title": "Equipment name",
      "titleVal":"equipment name",
      "numOfHeroes": [
        {
          "index": 0,
          "sum": "+7",
          "expand": True,
         "heroesUserAttachedToSet": [ ]
        }
      ],
      "changeTitleBtnLayout":{"disabled":True},
      "changeTitleTxtF":{"value":"", "autoFocus":True},
      "chipLayout":{"size":"small"},
      "expand": False,
      "heroData": [
          {
              "index": 0,
              "name": "Beatrix",
              "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 1,
              "name": "Brody",
              "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 2,
              "name": "Bruno",
              "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 3,
              "name": "Claude",
              "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 4,
              "name": "Clint",
              "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 5,
              "name": "Granger",
              "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
  
            {
              "index": 6,
              "name": "Beatrix",
              "img": "https://static.expertwm.com/mlbb/heroes/beatrix.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 7,
              "name": "Brody",
              "img": "https://static.expertwm.com/mlbb/heroes/brody.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 8,
              "name": "Bruno",
              "img": "https://static.expertwm.com/mlbb/heroes/bruno.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 9,
              "name": "Claude",
              "img": "https://static.expertwm.com/mlbb/heroes/claude.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 10,
              "name": "Clint",
              "img": "https://static.expertwm.com/mlbb/heroes/clint.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
            {
              "index": 11,
              "name": "Granger",
              "img": "https://static.expertwm.com/mlbb/heroes/granger.png?w=64",
               "clicked":False, "Layout":{"color":"default"}
            },
      ],
      "equippmentList": [
        {
          "index": 0,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 1,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 2,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 3,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 4,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        },
        {
          "index": 5,
          "name": "Tough Boots",
          "img": "https://static.expertwm.com/mlbb/items/tough-boots.png"
        }
      ],
      "equipmentCategory": [
        { "index": 0, "name": "Attack", "color": "#880808" },
        { "index": 1, "name": "Magic", "color": "#0047AB" },
        { "index": 2, "name": "Defense", "color": "#50C878" }
        # { "index": 3, "name": "Movement", "color": "#C19A6B" },
        # { "index": 4, "name": "Jungling", "color": "#702963" },
        # { "index": 5, "name": "Roaming", "color": "#40B5AD" }
      ],
      "top3Equipment": [
        { "index": 0, "name": "Health", "stat": "+4453" },
        { "index": 1, "name": "Magic Power", "stat": "+589" },
        { "index": 2, "name": "Atk Speed", "stat": "+33%" }
      ],
      "bottom3Equipment": [
        { "index": 0, "name": "Health", "stat": "+4453" },
        { "index": 1, "name": "Magic Power", "stat": "+589" },
        { "index": 2, "name": "Atk Speed", "stat": "+33%" }
      ],
      "expandData": [
        {
          "index": 0,
          "tabTitle": "Visualize",
          "toggle": False,
          "vizualizeD": [
            {
              "index": 0,
              "equipCatChecked": False,
              "dataToDisplayOriginal": [
                {
                  "skillFeature": "Attack_Speed",
                  "total": 190,
                  "attack": 20,
                  "magic": 30,
                  "defense": 30,
                  "movement": 70,
                  "jungling": 15,
                  "roaming": 15
                },
                {
                  "skillFeature": "CD_Reduction",
                  "total": 100,
                  "attack": 20,
                  "magic": 30,
                  "defense": 10,
                  "movement": 10,
                  "jungling": 15,
                  "roaming": 15
                },
                {
                  "skillFeature": "Crit_Chance",
                  "total": 50,
                  "attack": 20,
                  "magic": 5,
                  "defense": 5,
                  "movement": 5,
                  "jungling": 5,
                  "roaming": 10
                }
              ],
              "keysOrigin": [
                "total",
                "attack",
                "magic",
                "defense",
                "movement",
                "jungling",
                "roaming"
              ],
              "dataToDisplayCat": [
                {
                  "skillFeature": "Attack_Speed",
                  "total": 190,
                  "attack": 20,
                  "magic": 30,
                  "defense": 30,
                  "movement": 70,
                  "jungling": 15,
                  "roaming": 15
                },
                {
                  "skillFeature": "CD_Reduction",
                  "total": 100,
                  "attack": 20,
                  "magic": 30,
                  "defense": 10,
                  "movement": 10,
                  "jungling": 15,
                  "roaming": 15
                },
                {
                  "skillFeature": "Crit_Chance",
                  "total": 50,
                  "attack": 20,
                  "magic": 5,
                  "defense": 5,
                  "movement": 5,
                  "jungling": 5,
                  "roaming": 10
                }
              ],
              "chartLayout": {
                "keys": ["total"],
                "indexBy": "skillFeature",
                "margin": { "right": 85, "bottom": 40, "left": 30, "top": 20 },
                "labelSkipHeight": 12,
                "legends": [
                  {
                    "dataFrom": "keys",
                    "anchor": "bottom-right",
                    "direction": "column",
                    "justify": False,
                    "translateX": 100,
                    "translateY": 0,
                    "itemsSpacing": 2,
                    "itemWidth": 100,
                    "itemHeight": 20,
                    "itemDirection": "left-to-right",
                    "itemOpacity": 0.85,
                    "symbolSize": 20,
                    "effects": [
                      {
                        "on": "hover",
                        "style": {
                          "itemOpacity": 1
                        }
                      }
                    ]
                  }
                ]
              }
            }
          ],
          "gridD": [
            { "index": 0, "name": "Attack_Speed", "stat": "34%" },
            { "index": 1, "name": "CD_Reduction", "stat": "8%" },
            { "index": 2, "name": "Crit_Chance", "stat": "14%" },
            { "index": 3, "name": "HP", "stat": "4560" },
            { "index": 4, "name": "HP_Regen", "stat": "8" },
            { "index": 5, "name": "Hybrid_Lifesteal", "stat": "8" },
            { "index": 6, "name": "Lifesteal", "stat": "12" },
            { "index": 7, "name": "Magic_Defense", "stat": "115" },
            { "index": 8, "name": "Magic_Lifesteal", "stat": "7" },
            { "index": 9, "name": "Magic_PEN", "stat": "25%" },
            { "index": 10, "name": "Magic_Power", "stat": "308" },
            { "index": 11, "name": "Mana", "stat": "100" },
            { "index": 12, "name": "Mana_Regen", "stat": "8" },
            { "index": 13, "name": "Movement_Speed", "stat": "70" },
            { "index": 14, "name": "Physical_Attack", "stat": "689" },
            { "index": 15, "name": "Physical_Defense", "stat": "350" },
            { "index": 16, "name": "Spell_Vamp", "stat": "8" }
          ]
        }
      ]
    },
     
    ]


    
    num_clicks = card_component(data=data, showAdd=True, addHeroComponent=True, showHero=True, showChartSwitch=False, saveEdits=False, EditDashboard=True, userSetRating=False, key="foo_")
    
