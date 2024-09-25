from dataclasses import dataclass, field



@dataclass(kw_only=True)
class Data:
    card_use_count: dict[str, int] = field(default_factory=dict) #check
    hit_count: dict[str, int] = field(default_factory=dict) #check
    damage_dealt: dict[str, int] = field(default_factory=dict) #check
    damage_taken_count: dict[str, int] = field(default_factory=dict) #check
    damage_taken: dict[str, int] = field(default_factory=dict) #check
    scored: dict[str, int] = field(default_factory=dict)
    ability_count: dict[str, int] = field(default_factory=dict) #check
    healing_amount: dict[str, int] = field(default_factory=dict) #check
    use_heal_count: dict[str, int] = field(default_factory=dict) #check
    move_count: dict[str, int] = field(default_factory=dict) #check
    use_move_count: dict[str, int] = field(default_factory=dict) #check
    cube_used_count: dict[str, int] = field(default_factory=dict) #check
    killed_count: dict[str, int] = field(default_factory=dict) #check
    death_count: dict[str, int] = field(default_factory=dict) #check
    use_token_count: dict[str, int] = field(default_factory=dict) #check
    score_records: list[int] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        self.data_dicts = {"card_use_count": self.card_use_count, "hit_count": self.hit_count, "damage_dealt": self.damage_dealt, "damage_taken_count": self.damage_taken_count, "damage_taken": self.damage_taken,
                      "scored": self.scored, "ability_count": self.ability_count, "healing_amount": self.healing_amount, "heal_count": self.use_heal_count, "move_count": self.move_count,
                      "move_count": self.move_count, "use_move_count": self.use_move_count, "cube_used_count": self.cube_used_count, "killed_count": self.killed_count, "death_count": self.death_count,
                      "use_token_count": self.use_token_count}
    
    def data_update(self, data_name: str, name: str, value: int) -> None:
        print(self.data_dicts)
        if data_name in self.data_dicts:
            if name in self.data_dicts[data_name]:
                self.data_dicts[data_name][name] += value
            else:
                self.data_dicts[data_name][name] = value
        else:
            print(f"unknown data_name for key: {data_name}")