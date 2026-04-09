# BookMyJuice - Pricing Structure

**Source:** pricing table1.xlsx  
**Last Updated:** March 27, 2026  
**Currency:** INR (₹)

---

## 📊 Pricing Table

### Delight Category (Entry-Level)

| Size | Regular Price | Weekly (6 days) | Monthly (24 days) | Monthly Savings |
|------|--------------|-----------------|-------------------|-----------------|
| 200ml | ₹129 | ₹75/bottle (₹450 total) | ₹69/bottle (₹1,656 total) | ₹114 |
| 300ml | ₹159 | ₹99/bottle (₹594 total) | ₹89/bottle (₹2,136 total) | ₹168 |
| 500ml | ₹220 | ₹169/bottle (₹1,014 total) | ₹149/bottle (₹3,576 total) | ₹444 |

### Signature Category (Mid-Range)

| Size | Regular Price | Weekly (6 days) | Monthly (24 days) | Monthly Savings |
|------|--------------|-----------------|-------------------|-----------------|
| 200ml | ₹141.90 | ₹80/bottle (₹480 total) | ₹75/bottle (₹1,800 total) | ₹139.20 |
| 300ml | ₹174.90 | ₹105/bottle (₹630 total) | ₹95/bottle (₹2,280 total) | ₹199.20 |
| 500ml | ₹242 | ₹173/bottle (₹1,038 total) | ₹169/bottle (₹4,056 total) | ₹456 |

### Premium Category (Highest)

| Size | Regular Price | Weekly (6 days) | Monthly (24 days) | Monthly Savings |
|------|--------------|-----------------|-------------------|-----------------|
| 200ml | ₹156.09 | ₹90/bottle (₹540 total) | ₹83/bottle (₹1,992 total) | ₹144.84 |
| 300ml | ₹192.39 | ₹109/bottle (₹654 total) | ₹99/bottle (₹2,376 total) | ₹193.44 |
| 500ml | ₹266.20 | ₹183/bottle (₹1,098 total) | ₹179/bottle (₹4,296 total) | ₹496.80 |

---

## 📝 Pricing Notes

1. **Weekly Subscription:** 6 bottles (6 days of delivery)
2. **Monthly Subscription:** 24 bottles (4 weeks × 6 days)
3. **Monthly Savings:** 15-20% discount compared to weekly pricing
4. **2% Overhead:** Applied to subscription totals for payment processing
5. **Category Hierarchy:** Delight < Signature < Premium (ascending prices)

---

## 💡 UI/UX Requirements

### Category Visualization
- Display all three categories clearly (Delight, Signature, Premium)
- Use visual hierarchy (cards, colors, badges)
- Show price progression clearly
- Enable easy size selection (200ml, 300ml, 500ml)

### Plan Comparison
- Side-by-side Weekly vs Monthly comparison
- Show per-bottle pricing
- Highlight monthly savings prominently
- Use "Best Value" badge for monthly plans

### Price Display Format
```
Delight - 200ml
━━━━━━━━━━━━━━━━━━━━━━
Weekly:   ₹75/bottle  (₹450 total)
Monthly:  ₹69/bottle  (₹1,656 total)
          Save ₹114!  ⭐ Best Value
```

---

## 🎯 Subscription Plan Details

### Weekly Plan
- **Duration:** 6 days (1 week)
- **Deliveries:** 6 bottles
- **Best For:** First-time subscribers, trial period
- **Commitment:** Low commitment, flexible

### Monthly Plan
- **Duration:** 24 days (4 weeks)
- **Deliveries:** 24 bottles
- **Best For:** Regular customers, committed users
- **Savings:** ₹100-500 vs weekly plans
- **Commitment:** Monthly recurring

---

## 📱 Mobile App Implementation

### Pricing Display Screens
1. **Plan Selection Screen** - Show all 3 categories
2. **Product Detail Screen** - Size selection with pricing
3. **Cart Screen** - Show subscription totals
4. **Checkout Screen** - Final pricing breakdown

### Key Pricing Information to Display
- ✅ Per-bottle price (weekly & monthly)
- ✅ Total subscription cost
- ✅ Monthly savings amount
- ✅ Number of deliveries
- ✅ Category badge (Delight/Signature/Premium)
- ✅ Size selector (200ml/300ml/500ml)

---

**Reference File:** `x:\BMJ\pricing table1.xlsx`  
**Next Review:** After beta launch feedback
