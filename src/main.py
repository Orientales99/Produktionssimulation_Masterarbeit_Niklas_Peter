from src.data.production import Production

production = Production()

production.build_layout(30, 30)
print(production.print_layout(30, 30))