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
- [x] calculate fan
- [ ] class for each tile instead of writing out chinese character
- [ ] performance bench
  - [ ] per round time
  - [ ] search dp/winning hand
- [ ] numpy or equivalent matrix operation
- [ ] save state
  - [ ] replay with state
- [x] elagant prints
  - [ ] discard tiles segregated by players in sequence
- [ ] play action
  - [ ] move discard out? (less for loops)

## test strategy

- `test_fan.py` focus on 100% coverage of real hands
- non `test_calculate_fan.py::test_calculate_fan` focus on `ResultFan`
- `test_calculate_fan.py::test_calculate_fan` focus on all 82 combinations


```bash
>> python -m pytest --cov=. --cov-report html tests/
```

## RL thoughts

predict best next board to infer action.
how to run multiple RL agents and have gradient descent?
4 (peng + max 3 shang combination) * 13 (discards) action space size
using softmax to force probablity to sum up to one, and ensure
irrelevant actions are 0
