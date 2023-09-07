
# repleno

Repleno allows you to easily answer supply chain questions considering bill of
materials (BOM) structure.

- **PyPI**: https://pypi.org/project/repleno/ 
- **Source code**: 
- **Documentation**: 
- **Bug reports**: 


It answers the following questions:

1. "Which finished/purchased goods are associated with this stock keeping unit (SKU)?"
2. "Based on this master production schedule (MPS), which specific SKU quantities should be ordered from suppliers?"
3. "Using the master requirements planning (MRP) results and current supplier orders, when will there be stock-out periods?"
4. "If I discontinue SKU X, which other SKU's will also need to be discontinued?"

By providing:

- efficient queries about parent-child relationships for SKUs in the BOM
- MRP simulations to analyze the impact of MPS changes on purchase orders to suppliers
- inventory levels over a specific time periods
- identification of collateral SKU's that need to be phased-out along with a specific SKU


Installing:

```bash
python -m pip install requests
```

## Roadmap:

1. Integrate phantom scenarios to `run_mrp` and `get_lineage` and `get_collaterals` methods;
2. issue a warning when a parameter is not being loaded or a column has not been found;
3. get_collaterals function should return a tree, so it can be used to fully deplete the inventory inside it;
4. run special mrp for scenarios: produce all inventory left in the BOM (placing more order to deplete everything or with scrapage);
5. method for propagating any general label from roots to child nodes (from fininshed goods to purchased goods, in supply chain terms);
6. Method for quickly answering the question: if one component goes out of stock, what's the impact on the finished goods?
7. per component, shows how much of its demand impact finished goods. If 1 component goes into only 1 FG, then 100%
8. Add support to add lead times in different units (currently only support calendar days), like weeks or months
