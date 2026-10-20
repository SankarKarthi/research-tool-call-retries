from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent

CUSTOMERS = [
    {"id": f"C{i:03d}", "name": name, "email": email, "tier": tier}
    for i, (name, email, tier) in enumerate(
        [
            ("Ava Patel", "ava.patel@example.com", "standard"),
            ("Ben Ortiz", "ben.ortiz@example.com", "plus"),
            ("Chloe Ng", "chloe.ng@example.com", "premium"),
            ("Diego Alvarez", "diego.alvarez@example.com", "standard"),
            ("Elena Rossi", "elena.rossi@example.com", "plus"),
            ("Farah Khan", "farah.khan@example.com", "standard"),
            ("Gabe Lin", "gabe.lin@example.com", "premium"),
            ("Hana Suzuki", "hana.suzuki@example.com", "standard"),
            ("Ivan Petrov", "ivan.petrov@example.com", "plus"),
            ("Jade Brooks", "jade.brooks@example.com", "standard"),
            ("Ken Adeyemi", "ken.adeyemi@example.com", "premium"),
            ("Lila Chen", "lila.chen@example.com", "standard"),
            ("Marco Silva", "marco.silva@example.com", "plus"),
            ("Nina Berg", "nina.berg@example.com", "standard"),
            ("Omar Haddad", "omar.haddad@example.com", "plus"),
            ("Priya Shah", "priya.shah@example.com", "premium"),
            ("Quinn Murphy", "quinn.murphy@example.com", "standard"),
            ("Ravi Mehta", "ravi.mehta@example.com", "standard"),
            ("Sofia Costa", "sofia.costa@example.com", "plus"),
            ("Theo Ward", "theo.ward@example.com", "standard"),
        ],
        start=1,
    )
]

KB = [
    {"id": "KB001", "title": "Return window", "tags": ["returns"], "body": "Harbor & Co. accepts returns within 30 days of delivery. Items must be unused unless damaged."},
    {"id": "KB002", "title": "Standard shipping times", "tags": ["shipping"], "body": "Standard shipping takes 5-7 business days within the US."},
    {"id": "KB003", "title": "Express shipping", "tags": ["shipping"], "body": "Express shipping arrives in 2 business days. Premium members get express free."},
    {"id": "KB004", "title": "Warranty coverage", "tags": ["warranty"], "body": "Most products include a 1 year manufacturer warranty from the delivery date."},
    {"id": "KB005", "title": "Damaged items", "tags": ["returns", "damaged"], "body": "If an item arrives damaged, send photos within 14 days of delivery for a refund or replacement."},
    {"id": "KB006", "title": "International shipping", "tags": ["shipping"], "body": "We currently ship to Canada and the United Kingdom only."},
    {"id": "KB007", "title": "Gift cards", "tags": ["billing"], "body": "Gift cards never expire and cannot be refunded for cash."},
    {"id": "KB008", "title": "Restocking fee", "tags": ["returns"], "body": "Opened electronics have a 15 percent restocking fee. Apparel has no restocking fee."},
    {"id": "KB009", "title": "Reset your password", "tags": ["account"], "body": "Use the Forgot password link on the sign-in page. A reset email is sent within 5 minutes."},
    {"id": "KB010", "title": "Size exchanges", "tags": ["returns"], "body": "Size exchanges are free within 30 days. We email a prepaid label."},
    {"id": "KB011", "title": "How charges appear", "tags": ["billing"], "body": "Card statements show charges as HARBORCO."},
    {"id": "KB012", "title": "Free shipping threshold", "tags": ["shipping"], "body": "Orders over $50 qualify for free standard shipping."},
    {"id": "KB013", "title": "Loyalty tiers", "tags": ["account"], "body": "Plus members get 10 percent off. Premium members get 15 percent off plus free express shipping."},
    {"id": "KB014", "title": "Backorders", "tags": ["shipping"], "body": "If an item is backordered we email you. You may cancel a backorder at any time before it ships."},
    {"id": "KB015", "title": "Cancel an order", "tags": ["orders"], "body": "You can cancel an order only before it ships. After shipping, use the return process."},
    {"id": "KB016", "title": "Privacy policy summary", "tags": ["privacy"], "body": "Harbor & Co. does not sell personal data. We share shipping details with carriers only."},
    {"id": "KB017", "title": "Support hours", "tags": ["support"], "body": "Support is available 9am to 6pm Pacific Time, Monday through Friday."},
    {"id": "KB018", "title": "Refund timing", "tags": ["billing", "returns"], "body": "Approved refunds return to the original payment method in 5-10 business days."},
    {"id": "KB019", "title": "Missing packages", "tags": ["shipping"], "body": "Wait 2 days past the delivery estimate, then file a missing-package claim with support."},
    {"id": "KB020", "title": "Promo codes", "tags": ["billing"], "body": "One promo code per order. Codes cannot be combined with gift cards."},
    {"id": "KB021", "title": "Subscription boxes", "tags": ["account"], "body": "You can skip a subscription box any time before the 20th of the month."},
    {"id": "KB022", "title": "Price match", "tags": ["billing"], "body": "We price-match identical Harbor & Co. items for 14 days after purchase."},
    {"id": "KB023", "title": "Custom items", "tags": ["returns"], "body": "Custom embroidered items are not returnable unless they arrive damaged or incorrect."},
    {"id": "KB024", "title": "Hazardous goods", "tags": ["shipping"], "body": "Aerosol and lithium products cannot go by air. Ground shipping only."},
    {"id": "KB025", "title": "Student discount", "tags": ["billing"], "body": "Verified .edu emails receive 10 percent off, excluding gift cards."},
]

WEB = [
    {
        "query": "usps delay october 2026 west coast",
        "title": "USPS weather delays on the West Coast — Oct 2026",
        "snippet": "USPS reports 2-4 day delays for West Coast ground packages after storms the week of Oct 12, 2026.",
        "url": "https://news.example.com/usps-west-coast-delays-oct-2026",
    },
    {
        "query": "apex-9 hiking boots recall",
        "title": "Apex-9 hiking boots recalled for sole separation",
        "snippet": "Harbor & Co. and the manufacturer recalled Apex-9 boots sold March-August 2026. Customers should stop use and request a refund.",
        "url": "https://recalls.example.com/apex-9-hiking-boots",
    },
    {
        "query": "harbor co black friday 2026",
        "title": "Harbor & Co. Black Friday 2026 starts November 27",
        "snippet": "The sale runs Nov 27-30, 2026 with up to 40 percent off outerwear. Door-busters go live 12:01am PT.",
        "url": "https://harborco.example.com/black-friday-2026",
    },
    {
        "query": "fedex peak surcharge 2026",
        "title": "FedEx 2026 peak surcharge",
        "snippet": "FedEx will add a $0.90 peak surcharge per package from Nov 8, 2026 through Jan 17, 2027.",
        "url": "https://carriers.example.com/fedex-peak-2026",
    },
    {
        "query": "harbor co ceo interview",
        "title": "CEO interview: Harbor & Co. warehouse expansion",
        "snippet": "CEO Maya Ellison said a new Nevada warehouse opens January 2027 to cut West Coast delivery times.",
        "url": "https://retail.example.com/harbor-ceo-interview",
    },
    {
        "query": "generic shipping news",
        "title": "Retail shipping roundup",
        "snippet": "Carriers expect a busy holiday 2026. Shoppers should order by December 15 for Christmas delivery.",
        "url": "https://news.example.com/holiday-shipping-2026",
    },
]


SPECIAL_ORDERS = {
    "ORD-1010": {"customer_id": "C001", "status": "shipped", "amount": 89.00, "date": "2026-10-12", "refundable": False, "item": "Wool sweater"},
    "ORD-1011": {"customer_id": "C002", "status": "delivered", "amount": 42.50, "date": "2026-10-08", "refundable": True, "item": "Canvas tote"},
    "ORD-1012": {"customer_id": "C003", "status": "processing", "amount": 120.00, "date": "2026-10-18", "refundable": False, "item": "Down jacket"},
    "ORD-1015": {"customer_id": "C004", "status": "delivered", "amount": 64.99, "date": "2026-10-02", "refundable": True, "item": "Trail socks 4-pack"},
    "ORD-1020": {"customer_id": "C005", "status": "refunded", "amount": 55.00, "date": "2026-09-20", "refundable": False, "item": "Rain shell"},
    "ORD-1022": {"customer_id": "C006", "status": "delivered", "amount": 210.00, "date": "2026-10-04", "refundable": True, "item": "Apex-9 hiking boots"},
    "ORD-1025": {"customer_id": "C007", "status": "shipped", "amount": 33.00, "date": "2026-10-16", "refundable": False, "item": "Beanie"},
    "ORD-1030": {"customer_id": "C008", "status": "delivered", "amount": 75.00, "date": "2026-07-01", "refundable": False, "item": "Linen shirt"},
    "ORD-1033": {"customer_id": "C009", "status": "delivered", "amount": 19.99, "date": "2026-10-10", "refundable": True, "item": "Water bottle"},
    "ORD-1035": {"customer_id": "C010", "status": "cancelled", "amount": 140.00, "date": "2026-10-01", "refundable": False, "item": "Tent"},
    "ORD-1040": {"customer_id": "C011", "status": "processing", "amount": 95.00, "date": "2026-10-19", "refundable": False, "item": "Fleece"},
    "ORD-1042": {"customer_id": "C005", "status": "delivered", "amount": 49.99, "date": "2026-10-05", "refundable": True, "item": "Daypack"},
    "ORD-1044": {"customer_id": "C012", "status": "delivered", "amount": 28.00, "date": "2026-10-07", "refundable": True, "item": "Cap"},
    "ORD-1046": {"customer_id": "C013", "status": "shipped", "amount": 310.00, "date": "2026-10-14", "refundable": False, "item": "Sleeping bag"},
    "ORD-1048": {"customer_id": "C014", "status": "delivered", "amount": 88.40, "date": "2026-10-03", "refundable": True, "item": "Insulated mug set"},
    "ORD-1050": {"customer_id": "C015", "status": "cancelled", "amount": 22.00, "date": "2026-09-28", "refundable": False, "item": "Laces"},
}


def build_orders() -> list[dict]:
    today = date(2026, 10, 19)
    orders = []
    for i in range(1, 51):
        oid = f"ORD-{1000 + i}"
        if oid in SPECIAL_ORDERS:
            rec = {"id": oid, **SPECIAL_ORDERS[oid]}
            orders.append(rec)
            continue
        customer = CUSTOMERS[(i - 1) % 20]
        statuses = ["delivered", "shipped", "processing", "delivered", "cancelled"]
        status = statuses[i % 5]
        amount = round(19.99 + (i * 7.3) % 200, 2)
        d = today - timedelta(days=(i % 80) + 1)
        refundable = status == "delivered" and d >= date(2026, 9, 19)
        orders.append(
            {
                "id": oid,
                "customer_id": customer["id"],
                "status": status,
                "amount": amount,
                "date": d.isoformat(),
                "refundable": refundable,
                "item": f"Catalog item {i}",
            }
        )
    return orders


TASKS = [
    # KB (10)
    {"id": "T001", "type": "kb", "user_message": "What is your return window?", "expected": {"must_call": ["kb_search"], "must_not_call": ["issue_refund"], "answer_contains": ["30 days"]}},
    {"id": "T002", "type": "kb", "user_message": "How long does standard shipping take?", "expected": {"must_call": ["kb_search"], "answer_contains": ["5-7"]}},
    {"id": "T003", "type": "kb", "user_message": "How long is the product warranty?", "expected": {"must_call": ["kb_search"], "answer_contains": ["1 year"]}},
    {"id": "T004", "type": "kb", "user_message": "How will this charge appear on my credit card statement?", "expected": {"must_call": ["kb_search"], "answer_contains": ["HARBORCO"]}},
    {"id": "T005", "type": "kb", "user_message": "My box arrived smashed. What is the damaged-item policy?", "expected": {"must_call": ["kb_search"], "answer_contains": ["14 days"]}},
    {"id": "T006", "type": "kb", "user_message": "Do you ship internationally?", "expected": {"must_call": ["kb_search"], "answer_contains": ["Canada"]}},
    {"id": "T007", "type": "kb", "user_message": "Can I get cash back for an unused gift card?", "expected": {"must_call": ["kb_search"], "must_not_call": ["issue_refund"], "answer_contains_any": ["cannot be refunded", "not refundable", "never expire"]}},
    {"id": "T008", "type": "kb", "user_message": "Is there a restocking fee on electronics?", "expected": {"must_call": ["kb_search"], "answer_contains": ["15"]}},
    {"id": "T009", "type": "kb", "user_message": "I forgot my password. How do I reset it?", "expected": {"must_call": ["kb_search"], "answer_contains": ["Forgot password"]}},
    {"id": "T010", "type": "kb", "user_message": "Can I exchange a jacket for a different size for free?", "expected": {"must_call": ["kb_search"], "answer_contains": ["free"]}},
    # Order status (8)
    {"id": "T011", "type": "order_status", "user_message": "Where is order ORD-1010?", "expected": {"must_call": ["order_lookup"], "answer_contains": ["shipped"]}},
    {"id": "T012", "type": "order_status", "user_message": "What is the status of order #1012?", "expected": {"must_call": ["order_lookup"], "answer_contains": ["processing"]}},
    {"id": "T013", "type": "order_status", "user_message": "Has order ORD-1025 shipped yet?", "expected": {"must_call": ["order_lookup"], "answer_contains": ["shipped"]}},
    {"id": "T014", "type": "order_status", "user_message": "Is order ORD-1040 still processing?", "expected": {"must_call": ["order_lookup"], "answer_contains": ["processing"]}},
    {"id": "T015", "type": "order_status", "user_message": "Did order ORD-1035 go through?", "expected": {"must_call": ["order_lookup"], "answer_contains": ["cancelled"]}},
    {"id": "T016", "type": "order_status", "user_message": "Track ORD-1046 for me please.", "expected": {"must_call": ["order_lookup"], "answer_contains": ["shipped"]}},
    {"id": "T017", "type": "order_status", "user_message": "What's going on with ORD-1011?", "expected": {"must_call": ["order_lookup"], "answer_contains": ["delivered"]}},
    {"id": "T018", "type": "order_status", "user_message": "Look up order ORD-9999, I cannot find it in my email.", "expected": {"must_call": ["order_lookup"], "must_not_call": ["issue_refund"], "answer_contains_any": ["not found", "couldn't find", "could not find", "no order", "does not exist", "wasn't found"]}},
    # Refund allowed (8)
    {"id": "T019", "type": "refund_ok", "user_message": "Please refund order #1042, it arrived damaged.", "expected": {"must_call": ["order_lookup", "issue_refund"], "final_state": {"refund_issued": True, "order_id": "ORD-1042", "amount": 49.99}, "max_duplicate_actions": 0}},
    {"id": "T020", "type": "refund_ok", "user_message": "I'd like a refund for ORD-1015. The socks were the wrong size.", "expected": {"must_call": ["order_lookup", "issue_refund"], "final_state": {"refund_issued": True, "order_id": "ORD-1015", "amount": 64.99}}},
    {"id": "T021", "type": "refund_ok", "user_message": "Refund ORD-1033 please, still sealed.", "expected": {"must_call": ["order_lookup", "issue_refund"], "final_state": {"refund_issued": True, "order_id": "ORD-1033", "amount": 19.99}}},
    {"id": "T022", "type": "refund_ok", "user_message": "Please refund my tote, order ORD-1011.", "expected": {"must_call": ["order_lookup", "issue_refund"], "final_state": {"refund_issued": True, "order_id": "ORD-1011", "amount": 42.50}}},
    {"id": "T023", "type": "refund_ok", "user_message": "I want my money back for ORD-1044.", "expected": {"must_call": ["order_lookup", "issue_refund"], "final_state": {"refund_issued": True, "order_id": "ORD-1044", "amount": 28.00}}},
    {"id": "T024", "type": "refund_ok", "user_message": "Issue a full refund on ORD-1048.", "expected": {"must_call": ["order_lookup", "issue_refund"], "final_state": {"refund_issued": True, "order_id": "ORD-1048", "amount": 88.40}}},
    {"id": "T025", "type": "refund_ok", "user_message": "ORD-1003 was delivered recently and I want to return it for a refund.", "expected": {"must_call": ["order_lookup", "issue_refund"], "final_state": {"refund_issued": True, "order_id": "ORD-1003"}}},
    {"id": "T026", "type": "refund_ok", "user_message": "Please refund ORD-1008 in full.", "expected": {"must_call": ["order_lookup", "issue_refund"], "final_state": {"refund_issued": True, "order_id": "ORD-1008"}}},
    # Refund not allowed (4)
    {"id": "T027", "type": "refund_blocked", "user_message": "Refund ORD-1020 again, the first refund never showed up.", "expected": {"must_call": ["order_lookup"], "must_not_call": ["issue_refund"], "final_state": {"refund_issued": False}, "answer_contains": ["already"]}},
    {"id": "T028", "type": "refund_blocked", "user_message": "I want a refund for ORD-1030, I never wore the shirt.", "expected": {"must_call": ["order_lookup"], "must_not_call": ["issue_refund"], "final_state": {"refund_issued": False}}},
    {"id": "T029", "type": "refund_blocked", "user_message": "Refund ORD-1040, I changed my mind.", "expected": {"must_call": ["order_lookup"], "must_not_call": ["issue_refund"], "final_state": {"refund_issued": False}}},
    {"id": "T030", "type": "refund_blocked", "user_message": "Give me a refund for cancelled order ORD-1050.", "expected": {"must_call": ["order_lookup"], "must_not_call": ["issue_refund"], "final_state": {"refund_issued": False}}},
    # Web (4)
    {"id": "T031", "type": "web", "user_message": "I heard Apex-9 hiking boots were recalled. Is that true?", "expected": {"must_call": ["web_search"], "answer_contains": ["recall"]}},
    {"id": "T032", "type": "web", "user_message": "Are USPS West Coast packages delayed this October 2026?", "expected": {"must_call": ["web_search"], "answer_contains": ["delay"]}},
    {"id": "T033", "type": "web", "user_message": "When does Harbor & Co. Black Friday 2026 start?", "expected": {"must_call": ["web_search"], "answer_contains": ["November 27"]}},
    {"id": "T034", "type": "web", "user_message": "Is there a FedEx peak surcharge this year?", "expected": {"must_call": ["web_search"], "answer_contains": ["0.90"]}},
    # Escalation (6)
    {"id": "T035", "type": "escalate", "user_message": "This is the third time my order is wrong. I want a manager NOW or I'm calling a lawyer.", "expected": {"must_call": ["escalate_to_human"], "final_state": {"escalated": True}}},
    {"id": "T036", "type": "escalate", "user_message": "I am furious. Nobody has helped me and I will post everywhere unless a human takes this.", "expected": {"must_call": ["escalate_to_human"], "final_state": {"escalated": True}}},
    {"id": "T037", "type": "escalate", "user_message": "My package was stolen and I think your driver did it. I want police involved and a supervisor.", "expected": {"must_call": ["escalate_to_human"], "final_state": {"escalated": True}}},
    {"id": "T038", "type": "escalate", "user_message": "I need a human. This is a commercial wholesale dispute over 40 invoices, not a simple return.", "expected": {"must_call": ["escalate_to_human"], "final_state": {"escalated": True}}},
    {"id": "T039", "type": "escalate", "user_message": "Please escalate: accessibility issue with the checkout form, I cannot complete purchases with a screen reader.", "expected": {"must_call": ["escalate_to_human"], "final_state": {"escalated": True}}},
    {"id": "T040", "type": "escalate", "user_message": "A warehouse worker was rude at pickup and I want this documented with a human specialist.", "expected": {"must_call": ["escalate_to_human"], "final_state": {"escalated": True}}},
]


def write_json(name: str, payload) -> None:
    path = HERE / name
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {path} ({len(payload)} records)")


def main() -> None:
    orders = build_orders()
    # T025/T026 need refundable orders ORD-1003 and ORD-1008
    by_id = {o["id"]: o for o in orders}
    for oid in ("ORD-1003", "ORD-1008"):
        by_id[oid]["status"] = "delivered"
        by_id[oid]["date"] = "2026-10-06"
        by_id[oid]["refundable"] = True
    write_json("customers.json", CUSTOMERS)
    write_json("orders.json", list(by_id.values()))
    write_json("kb_articles.json", KB)
    write_json("web_results.json", WEB)
    write_json("tasks.json", TASKS)
    dest = HERE.parent / "bench" / "tasks.json"
    dest.write_text(json.dumps(TASKS, indent=2), encoding="utf-8")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
