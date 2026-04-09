TARGET := darwin_sensor
BPF_OBJ := $(TARGET).bpf.o

all: $(BPF_OBJ) vmlinux.h

# Generate vmlinux.h from the current system kernel
vmlinux.h:
	bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h

# Compile BPF code to object file
$(BPF_OBJ): $(TARGET).bpf.c vmlinux.h
	clang -g -O2 -target bpf -D__TARGET_ARCH_x86 -c $(TARGET).bpf.c -o $(BPF_OBJ)

clean:
	rm -f $(BPF_OBJ) vmlinux.h
