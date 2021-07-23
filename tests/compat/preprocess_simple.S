#define GPIO 2
#define BASE 0x100
#define ADDR (BASE + GPIO)

entry:
  move r0, GPIO
  move r1, ADDR
