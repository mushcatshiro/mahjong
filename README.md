# mahjong

mahjong in python. two modes provided, visualized client and api client.

## features

- [ ] api client
- [ ] visualized client
- [ ] all winning conditions
- [ ] helpers/suggestions
  - [ ] combinations and their probability
- [ ] 24圈
  - [ ] 发牌顺序
  - [ ] 起手顺序
- [ ] class for each tile instead of writing out chinese character
- [ ] performance bench
  - [ ] per round time
  - [ ] search dp/winning hand
- [ ] numpy or equivalent matrix operation
- [ ] save state
  - [ ] replay with state

## test strategy

- `test_fan.py` focus on 100% coverage of real hands
- non `test_calculate_fan.py::test_calculate_fan` focus on `ResultFan`
- `test_calculate_fan.py::test_calculate_fan` focus on all 82 combinations
