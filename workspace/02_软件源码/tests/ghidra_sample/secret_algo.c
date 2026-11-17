/* P17 逆向模拟样本（模拟测试任务用，非真实业务源码）。
 *
 * 用法：先在有源码侧编译成 exe，再把 exe 交给 Ghidra 适配层逆向。
 * 验收标准（ground truth，只有本文件知道）：
 * 1. 逆向导出的函数清单里能认出 check_license / banner / main；
 * 2. check_license 的反编译 C 代码里出现魔数 1337；
 * 3. main 的反编译 C 里出现字符串 "ACCESS GRANTED"。
 * 满足三条 = 逆向链路端到端可用（L4）。
 */
#include <stdio.h>

int check_license(const char *key) {
    int sum = 0;
    for (int i = 0; key[i]; i++) {
        sum += key[i] * (i + 1);
    }
    return sum == 1337;
}

void banner(void) {
    printf("DEMO-APP v0.1\n");
}

int main(int argc, char **argv) {
    banner();
    if (argc > 1 && check_license(argv[1])) {
        printf("ACCESS GRANTED\n");
    } else {
        printf("ACCESS DENIED\n");
    }
    return 0;
}
