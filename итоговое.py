import pandas as pd


def load_data():
    df = pd.read_csv('Испытательное.csv')
    df['Месяц'] = df['Месяц'].astype(str)
    return df


def get_user_input(df):
    print("Доступные коды товаров:", df['Код ОКПД-2'].unique())
    product = input("Введите код товара: ")

    print("Доступные года:", (df['Год'].unique()))
    year1 = int(input("Введите первый год: "))
    year2 = int(input("Введите второй год: "))

    print("Доступные месяцы:", (df['Месяц'].unique()))
    month1 = input("Введите первый месяц: ")
    month2 = input("Введите второй месяц: ")

    return product, year1, year2, month1, month2


def process_data(df, product, year1, year2, month1, month2):
    # Фильтрация данных
    filtered = df[df['Код ОКПД-2'] == product]

    # Данные для первого периода
    period1 = filtered[(filtered['Год'] == year1) & (filtered['Месяц'] == month1)]
    p1 = period1.groupby('Округ')['Значение'].sum().reset_index()
    p1.rename(columns={'Значение': f'{year1}-{month1}'}, inplace=True)

    # Данные для второго периода
    period2 = filtered[(filtered['Год'] == year2) & (filtered['Месяц'] == month2)]
    p2 = period2.groupby('Округ')['Значение'].sum().reset_index()
    p2.rename(columns={'Значение': f'{year2}-{month2}'}, inplace=True)

    # Объединение данных
    merged = pd.merge(p1, p2, on='Округ', how='outer').fillna(0)

    # Добавление итоговой строки
    total_row = pd.DataFrame({
        'Округ': ['ВСЕ ОКРУГА'],
        f'{year1}-{month1}': [merged[f'{year1}-{month1}'].sum()],
        f'{year2}-{month2}': [merged[f'{year2}-{month2}'].sum()]
    })

    merged = pd.concat([total_row, merged], ignore_index=True)

    # Расчет дельты
    merged['∆, %'] = ((merged[f'{year2}-{month2}'] - merged[f'{year1}-{month1}']) /
                      merged[f'{year1}-{month1}'].replace(0, float('inf'))) * 100
    merged['∆, %'] = merged['∆, %'].round(2)

    # Сортировка
    merged.sort_values(by=f'{year2}-{month2}', ascending=False, inplace=True)

    return merged.reset_index(drop=True)


def main():
    df = load_data()

    product, year1, year2, month1, month2 = get_user_input(df)

    result = process_data(df, product, year1, year2, month1, month2)

    print(f"\nРезультат анализа для товара {product}:")
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()