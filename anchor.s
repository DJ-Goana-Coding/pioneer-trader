// anchor.s - ARM64 Assembly heartbeat monitoring
// CPU affinity maintenance for trading nodes
// NO-OP loop implementation
//
// NOTE: This infinite loop is intentional for CPU affinity maintenance.
// It ensures dedicated CPU core availability for time-critical trading operations.
// Deploy in a containerized environment with CPU limits to control resource usage.

.global _start
.align 2

_start:
    // Initialize loop counter
    mov x0, #0

loop:
    // NO-OP instruction - maintains CPU affinity
    nop
    nop
    nop
    nop
    
    // Increment counter
    add x0, x0, #1
    
    // Continue loop indefinitely
    b loop

.section .note.GNU-stack,"",@progbits
