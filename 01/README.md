# Project 1: Boolean Logic

**Last updated: 28-12-2018**

## Projects:
### NAND Gate
NAND gate will be used as the fundamental building block for most logic gates in this nand2tetris course.

![NAND gate](pic/NAND.png)
| a | b | out |
| - | - | - |
| 0 | 0 | 1 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

### NOT Gate
![NOT gate](pic/NOT.png)
| in | out |
| - | - |
| 0 | 1 |
| 1 | 0 |

### AND Gate
![AND gate](pic/AND.png)
| a | b | out |
| - | - | - |
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

### OR Gate
![OR gate](pic/OR.png)
| a | b | out |
| - | - | - |
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

### XOR Gate
![XOR gate](pic/XOR.png)
| a | b | out |
| - | - | - |
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

### Multiplexor (MUX)
![MUX](pic/MUX.png)
| a | b | sel | out |
| - | - | - | - |
| 0 | 0 | **0** | 0 |
| 0 | 1 | **0** | 0 |
| 1 | 0 | **0** | 1 |
| 1 | 1 | **0** | 1 |
| 0 | 0 | **1** | 0 |
| 0 | 1 | **1** | 1 |
| 1 | 0 | **1** | 0 |
| 1 | 1 | **1** | 1 |

### Demultiplexor (DMUX)
![DMUX](pic/DMUX.png)
| in | sel | a | b |
| - | - | - | - |
| 0 | **0** | 0 | 0 |
| 0 | **1** | 0 | 0 |
| 1 | **0** | 1 | 0 |
| 1 | **1** | 0 | 1 |