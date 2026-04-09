#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

// Define the structure for the data we want to capture
struct event_t {
    u32 pid;
    char comm[16];
    u64 ts;
    u32 type;
};

// Define the output buffer to send data to userspace
BPF_PERF_OUTPUT(events);

// Hook into the execve syscall entry
int handle_execve(struct pt_regs *ctx) {
    struct event_t event = {};
    
    // Capture metadata
    event.pid = bpf_get_current_pid_tgid() >> 32;
    event.ts = bpf_ktime_get_ns();
    event.type = 0; // Type 0 = Process Execution
    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    // Submit to the performance buffer
    events.perf_submit(ctx, &event, sizeof(event));
    return 0;
}
