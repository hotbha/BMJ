# BookMyJuice - Pricing Structure

**Source:** pricing table1.xlsx (imported into Chargebee Product Catalog 2.0)  
**Last Updated:** 2026-05-25  
**Currency:** INR (₹)

---

## 📊 Pricing Table

> **Note:** All subscription prices are stored in Chargebee as total amounts (not per-bottle). The Flutter app displays per-bottle breakdown for user clarity. See chargebee import reference: pricing table1.xlsx.

### Delight Category (Entry-Level)

| Size | Regular Price (per bottle) | Weekly (6 bottles) | Monthly (24 bottles) | Monthly Savings |
|------|---------------------------|-------------------|---------------------|-----------------|
| 200ml | ₹129 | ₹774 | ₹3,096 | ₹0 |
| 300ml | ₹159 | ₹954 | ₹3,816 | ₹0 |
| 500ml | ₹229 | ₹1,374 | ₹5,496 | ₹0 |

### Signature Category (Mid-Range)

| Size | Regular Price (per bottle) | Weekly (6 bottles) | Monthly (24 bottles) | Monthly Savings |
|------|---------------------------|-------------------|---------------------|-----------------|
| 200ml | ₹199 | ₹1,194 | ₹4,776 | ₹0 |
| 300ml | ₹249 | ₹1,494 | ₹5,976 | ₹0 |
| 500ml | ₹349 | ₹2,094 | ₹8,376 | ₹0 |

### Premium Category (Highest)

| Size | Regular Price (per bottle) | Weekly (6 bottles) | Monthly (24 bottles) | Monthly Savings |
|------|---------------------------|-------------------|---------------------|-----------------|
| 200ml | ₹299 | ₹1,794 | ₹7,176 | ₹0 |
| 300ml | ₹349 | ₹2,094 | ₹8,376 | ₹0 |
| 500ml | ₹449 | ₹2,694 | ₹10,776 | ₹0 |

---

## 📝 Pricing Notes

1. **Weekly Subscription:** 6 bottles (6 days of delivery, period=6, periodUnit=day)
2. **Monthly Subscription:** 24 bottles (4 weeks × 6 days, period=1, periodUnit=month)
3. **Chargebee ItemPrice:** Total amount = base_price × quantity (Weekly = base × 6, Monthly = base × 24). Stored in paise in Chargebee; backend converts via `movePointLeft(2)`.
4. **Category Hierarchy:** Delight < Signature < Premium (ascending prices)
5. **Juice Varieties per Category:** 5 juices — Orange, Apple, Mango, Mixed, Black Grapes
6. **Sizes per Juice:** 200ml, 300ml, 500ml
7. **Total Items in Chargebee:** 45 (3 families × 5 juices × 3 sizes)
8. **Total ItemPrices in Chargebee:** 90 (45 items × Weekly + Monthly)
9. **Payment:** All payments are processed through **Chargebee hosted checkout WebView** only. No Razorpay direct integration.
10. **2% Overhead:** Applied by Chargebee at payment processing (Chargebee-side only). bmjServer receives the net amount after Chargebee fees.

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
