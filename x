package com.bookmyjuice.controllers;

import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bookmyjuice.models.User;
import com.bookmyjuice.models.dto.BottleLedgerEntry;
import com.bookmyjuice.models.entities.BottleTransactionEntity;
import com.bookmyjuice.repository.UserRepository;
import com.bookmyjuice.services.BottleTrackingService;
import com.bookmyjuice.services.UserDetailsImpl;

/**
 * REST Controller for Bottle Tracking operations.
 * 
 * Endpoints:
 * GET  /api/bottles/ledger       — Get computed bottle ledger (balance) for the current user
 * GET  /api/bottles/transactions — Get raw transaction history for the current user
 * POST /api/bottles/return       — Record bottles returned by the user
 * POST /api/bottles/broken       — Report bottles broken/lost by the user
 */
@RestController
@RequestMapping("/api/bottles")
public class BottleTrackingController {

    private static final Logger logger = LoggerFactory.getLogger(BottleTrackingController.class);

    @Autowired
    private BottleTrackingService bottleTrackingService;

    @Autowired
    private UserRepository userRepository;

    // ==================== GET: Ledger ====================

    /**
     * GET /api/bottles/ledger
     * Returns the computed BottleLedger for the authenticated user.
     * Each entry shows: bottle type, total issued, total returned, total broken, outstanding balance.
     */
    @GetMapping("/ledger")
    @PreAuthorize("hasRole('USER') or hasRole('MODERATOR') or hasRole('ADMIN')")
    public ResponseEntity<?> getLedger() {
        try {
            String customerId = getCustomerId();
            if (customerId == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("status", "error", "message", "User not authenticated"));
            }

            List<BottleLedgerEntry> ledger = bottleTrackingService.getLedger(customerId);
            return ResponseEntity.ok(Map.of(
                    "status", "success",
                    "data", ledger
            ));
        } catch (Exception e) {
            logger.error("Error fetching bottle ledger: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("status", "error", "message", e.getMessage()));
        }
    }

    // ==================== GET: Transactions ====================

    /**
     * GET /api/bottles/transactions
     * Returns the raw bottle transaction history for the authenticated user.
     */
    @GetMapping("/transactions")
    @PreAuthorize("hasRole('USER') or hasRole('MODERATOR') or hasRole('ADMIN')")
    public ResponseEntity<?> getTransactions() {
        try {
            String customerId = getCustomerId();
            if (customerId == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("status", "error", "message", "User not authenticated"));
            }

            List<BottleTransactionEntity> transactions = bottleTrackingService.getTransactions(customerId);
            return ResponseEntity.ok(Map.of(
                    "status", "success",
                    "count", transactions.size(),
                    "data", transactions
            ));
        } catch (Exception e) {
            logger.error("Error fetching bottle transactions: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("status", "error", "message", e.getMessage()));
        }
    }

    // ==================== POST: Return ====================

    /**
     * POST /api/bottles/return
     * Record bottles returned by the user.
     * 
     * Request body:
     * {
     *   "orderId": "ord_123",
     *   "bottleType": "glass_500ml",
     *   "quantity": 5,
     *   "referenceId": "pickup_456",
     *   "notes": "Collected by delivery partner"
     * }
     */
    @PostMapping("/return")
    @PreAuthorize("hasRole('USER') or hasRole('MODERATOR') or hasRole('ADMIN')")
    public ResponseEntity<?> recordReturn(@RequestBody Map<String, Object> request) {
        try {
            String customerId = getCustomerId();
            if (customerId == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("status", "error", "message", "User not authenticated"));
            }

            String orderId = getStringParam(request, "orderId");
            String bottleType = getStringParam(request, "bottleType");
            int quantity = getIntParam(request, "quantity");
            String referenceId = getStringParam(request, "referenceId");
            String notes = getStringParam(request, "notes");

            if (orderId == null || bottleType == null || quantity <= 0) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body(Map.of("status", "error", "message",
                                "Required fields: orderId, bottleType, quantity (> 0)"));
            }

            BottleTransactionEntity tx = bottleTrackingService.recordReturn(
                    orderId, customerId, bottleType, quantity, referenceId, notes);

            return ResponseEntity.ok(Map.of(
                    "status", "success",
                    "message", "Bottle return recorded",
                    "data", tx
            ));
        } catch (Exception e) {
            logger.error("Error recording bottle return: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("status", "error", "message", e.getMessage()));
        }
    }

    // ==================== POST: Broken ====================

    /**
     * POST /api/bottles/broken
     * Report bottles as broken or lost.
     * 
     * Request body:
     * {
     *   "orderId": "ord_123",
     *   "bottleType": "glass_500ml",
     *   "quantity": 2,
     *   "referenceId": "complaint_789",
     *   "notes": "2 bottles cracked during delivery"
     * }
     */
    @PostMapping("/broken")
    @PreAuthorize("hasRole('USER') or hasRole('MODERATOR') or hasRole('ADMIN')")
    public ResponseEntity<?> recordBroken(@RequestBody Map<String, Object> request) {
        try {
            String customerId = getCustomerId();
            if (customerId == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("status", "error", "message", "User not authenticated"));
            }

            String orderId = getStringParam(request, "orderId");
            String bottleType = getStringParam(request, "bottleType");
            int quantity = getIntParam(request, "quantity");
            String referenceId = getStringParam(request, "referenceId");
            String notes = getStringParam(request, "notes");

            if (orderId == null || bottleType == null || quantity <= 0) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body(Map.of("status", "error", "message",
                                "Required fields: orderId, bottleType, quantity (> 0)"));
            }

            BottleTransactionEntity tx = bottleTrackingService.recordBroken(
                    orderId, customerId, bottleType, quantity, referenceId, notes);

            return ResponseEntity.ok(Map.of(
                    "status", "success",
                    "message", "Bottle broken/lost report recorded",
                    "data", tx
            ));
        } catch (Exception e) {
            logger.error("Error recording broken bottle: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("status", "error", "message", e.getMessage()));
        }
    }

    // ==================== Helpers ====================

    private String getCustomerId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.getPrincipal() instanceof UserDetailsImpl) {
            UserDetailsImpl userDetails = (UserDetailsImpl) authentication.getPrincipal();
            return userDetails.getId().toString();
        }
        return null;
    }

    private String getStringParam(Map<String, Object> map, String key) {
        Object val = map.get(key);
        return val != null ? val.toString() : null;
    }

    private int getIntParam(Map<String, Object> map, String key) {
        Object val = map.get(key);
        if (val instanceof Number) return ((Number) val).intValue();
        if (val instanceof String) {
            try { return Integer.parseInt((String) val); } catch (NumberFormatException e) { return 0; }
        }
        return 0;
    }
}
