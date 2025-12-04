import { useState } from 'react'

export default function App() {
  const [activePhase, setActivePhase] = useState(0)
  const [activeTab, setActiveTab] = useState('parsing')
  const [openRisk, setOpenRisk] = useState(null)
  const [openFR, setOpenFR] = useState(null)

  const phases = [
    { 
      name: 'Пилот', 
      title: 'Пилот: Перу + Методология',
      why: 'Валидируем подход на одном рынке с активной конкуренцией. Перу — идеальный кейс: InDriver силён, данные доступны, результат измерим.',
      impact: 'Понимание, работает ли подход. Первые инсайты по конкурентам. Фундамент для автоматизации.',
      items: [
        'Сбор данных из открытых источников (сайты, отзывы, релиз-ноты)',
        'Классификация и структурирование информации',
        'Сравнительный анализ продуктов и тарифов',
        'Формирование гипотез для продуктовой команды',
        'PRD-документ для воспроизведения процесса'
      ] 
    },
    { 
      name: 'Автоматизация', 
      title: 'Автоматизация сбора данных',
      why: 'Ручной сбор не масштабируется. Автоматизация даёт регулярность и скорость, которые невозможны вручную.',
      impact: 'Еженедельные обновления без ручной работы. Команда фокусируется на анализе, не на сборе.',
      items: [
        'Автоматический парсинг источников (1 раз в неделю или чаще)',
        'Детекция изменений и новых данных',
        'Алерты по важным событиям',
        'API для интеграции с внутренними системами'
      ] 
    },
    { 
      name: 'Источники', 
      title: 'Расширение источников',
      why: 'Открытые данные — это верхушка айсберга. Чаты водителей, закрытые группы — там реальные инсайты.',
      impact: 'Глубина понимания конкурентов x3. Доступ к информации, которую не видят другие.',
      items: [
        'Подключение чатов водителей (Telegram, WhatsApp)',
        'Мониторинг закрытых групп',
        'Работа с платными источниками данных'
      ] 
    },
    { 
      name: 'Дашборды', 
      title: 'Визуализация и дашборды',
      why: 'Данные без визуализации — это просто таблицы. Дашборды превращают данные в решения.',
      impact: 'C-level видит картину за 5 минут. Продукт принимает решения на основе данных.',
      items: [
        'Дашборды для продуктовой команды',
        'Дашборды для маркетинга',
        'Executive summary для C-level',
        'Кастомные отчёты по запросу'
      ] 
    },
    { 
      name: 'Scale', 
      title: 'Масштабирование',
      why: 'Архитектура пилота универсальна. Добавление региона = новый набор источников, та же логика.',
      impact: 'Покрытие всей географии Yango. Единая картина конкурентной среды.',
      items: [
        'СНГ (Россия, Казахстан, Узбекистан)',
        'Африка (ключевые рынки)',
        'Латам (за пределами Перу)',
        'Пакистан и Ближний Восток'
      ] 
    },
  ]

  const requirements = {
    parsing: [
      { 
        id: 'FR-001', 
        desc: 'Парсинг официальных сайтов конкурентов', 
        priority: 'must',
        why: 'Официальные сайты — первоисточник информации о продуктах и тарифах. Здесь публикуются изменения раньше, чем где-либо.',
        impact: 'Актуальная информация о продуктовых изменениях в течение 24-48 часов.',
        risk: 'Без этого работаем вслепую — узнаём об изменениях от пользователей или СМИ с задержкой.'
      },
      { 
        id: 'FR-002', 
        desc: 'Парсинг релиз-ноутов из App Store / Google Play', 
        priority: 'must',
        why: 'Релиз-ноты = roadmap конкурента в открытом доступе. Каждое обновление — сигнал о приоритетах.',
        impact: 'Понимание продуктовой стратегии конкурентов. Предсказание следующих шагов.',
        risk: 'Пропустим важные фичи, которые конкуренты тестируют.'
      },
      { 
        id: 'FR-003', 
        desc: 'Сбор и анализ отзывов пользователей (водители + пассажиры)', 
        priority: 'must',
        why: 'Отзывы — голос рынка. Что хвалят у конкурентов = их сильные стороны. Что критикуют = возможности для Yango.',
        impact: 'Карта сильных и слабых сторон каждого конкурента. Идеи для улучшения продукта.',
        risk: 'Принимаем решения без понимания реального восприятия рынка.'
      },
      { 
        id: 'FR-004', 
        desc: 'Мониторинг публичных чатов и форумов водителей', 
        priority: 'should',
        why: 'Водители обсуждают условия работы, сравнивают платформы. Это инсайдерская информация в открытом доступе.',
        impact: 'Понимание реальных условий для водителей у конкурентов. Рычаги для привлечения.',
        risk: 'Можно начать без этого, но потеряем важный слой информации.'
      },
      { 
        id: 'FR-005', 
        desc: 'Отслеживание новостей и пресс-релизов', 
        priority: 'should',
        why: 'Партнёрства, инвестиции, выход на новые рынки — всё это публикуется в СМИ.',
        impact: 'Стратегический контекст: куда движутся конкуренты в долгосрочной перспективе.',
        risk: 'Можно мониторить вручную, но это отнимает время аналитиков.'
      },
      { 
        id: 'FR-006', 
        desc: 'Парсинг закрытых Telegram-чатов водителей', 
        priority: 'nice',
        why: 'Самая ценная информация — в закрытых группах. Но доступ сложнее и требует отдельной работы.',
        impact: 'Эксклюзивные инсайты, недоступные конкурентам.',
        risk: 'Сложная реализация. Лучше сделать после стабилизации основного парсинга.'
      },
    ],
    analysis: [
      { 
        id: 'FR-007', 
        desc: 'Сравнительный анализ тарифов (водители)', 
        priority: 'must',
        why: 'Тарифы для водителей — ключевой фактор выбора платформы. Конкуренты постоянно их меняют.',
        impact: 'Понимание, как Yango выглядит на фоне конкурентов. Данные для оптимизации комиссий.',
        risk: 'Без этого не понимаем, почему водители уходят или приходят.'
      },
      { 
        id: 'FR-008', 
        desc: 'Сравнительный анализ тарифов (пассажиры)', 
        priority: 'must',
        why: 'Цена поездки = главный фактор для пассажира. Нужно знать, как мы выглядим относительно рынка.',
        impact: 'Данные для ценовой стратегии. Понимание эластичности спроса.',
        risk: 'Ценообразование вслепую, без понимания конкурентного контекста.'
      },
      { 
        id: 'FR-009', 
        desc: 'Отслеживание промо-акций и скидок', 
        priority: 'must',
        why: 'Промо — тактическое оружие. Конкуренты используют его для захвата доли рынка.',
        impact: 'Возможность реагировать на агрессивные промо. Данные для планирования своих акций.',
        risk: 'Узнаём о промо конкурентов от пользователей, когда уже поздно реагировать.'
      },
      { 
        id: 'FR-010', 
        desc: 'Классификация продуктовых изменений по категориям', 
        priority: 'must',
        why: 'Без классификации все изменения в одной куче. Нужно быстро находить релевантное.',
        impact: 'Фильтрация по типу: UX, тарифы, безопасность, водительский опыт и т.д.',
        risk: 'Ручная сортировка = потеря времени аналитиков.'
      },
      { 
        id: 'FR-011', 
        desc: 'Приоритизация по влиянию на бизнес', 
        priority: 'should',
        why: 'Не все изменения одинаково важны. Новая модель ценообразования важнее нового цвета кнопки.',
        impact: 'Фокус команды на том, что реально влияет на рынок.',
        risk: 'Можно жить без этого, но будете тратить время на незначительные изменения.'
      },
      { 
        id: 'FR-012', 
        desc: 'Сегментация отзывов по ролям и темам', 
        priority: 'should',
        why: 'Водители и пассажиры говорят о разном. Нужно разделять для правильного анализа.',
        impact: 'Точечные инсайты для каждого направления продукта.',
        risk: 'Общая каша из отзывов без возможности глубокого анализа.'
      },
    ],
    output: [
      { 
        id: 'FR-013', 
        desc: 'Еженедельный дайджест изменений', 
        priority: 'must',
        why: 'Регулярный формат = привычка команды смотреть на конкурентов. Без регулярности — забудут.',
        impact: 'Команда всегда в курсе. Не нужно спрашивать "а что там у конкурентов?"',
        risk: 'Информация собирается, но не доходит до тех, кто принимает решения.'
      },
      { 
        id: 'FR-014', 
        desc: 'Сравнительные таблицы по фичам и тарифам', 
        priority: 'must',
        why: 'Визуальное сравнение = быстрое понимание. Таблица говорит больше, чем текст.',
        impact: 'Быстрое понимание позиционирования каждого игрока.',
        risk: 'Текстовые отчёты читают долго и не запоминают.'
      },
      { 
        id: 'FR-015', 
        desc: 'Формирование гипотез для продуктовой команды', 
        priority: 'must',
        why: 'Данные без интерпретации — просто данные. Гипотезы = actionable insights.',
        impact: 'Продуктовая команда получает идеи, а не сырую информацию.',
        risk: 'Данные собираются, но не превращаются в действия.'
      },
      { 
        id: 'FR-016', 
        desc: 'Алерты по критичным изменениям', 
        priority: 'should',
        why: 'Некоторые изменения требуют немедленной реакции. Еженедельный дайджест — слишком медленно.',
        impact: 'Реакция на агрессивные действия конкурентов в течение часов, не дней.',
        risk: 'Можно жить без этого, но потеряете скорость реакции.'
      },
      { 
        id: 'FR-017', 
        desc: 'Интерактивные дашборды', 
        priority: 'nice',
        why: 'Дашборды позволяют самостоятельно исследовать данные. Но требуют инфраструктуры.',
        impact: 'Self-service аналитика для разных команд.',
        risk: 'Можно начать с отчётов. Дашборды — следующий этап.'
      },
    ],
    infra: [
      { 
        id: 'FR-018', 
        desc: 'Структурированная база данных изменений', 
        priority: 'must',
        why: 'Без базы данные теряются. Нужна история для анализа трендов.',
        impact: 'Возможность смотреть динамику: как менялись тарифы за год.',
        risk: 'Каждый раз собираем с нуля, теряем исторический контекст.'
      },
      { 
        id: 'FR-019', 
        desc: 'Документация процесса сбора (PRD)', 
        priority: 'must',
        why: 'Пилот должен быть воспроизводим. Без документации знания остаются в головах.',
        impact: 'Возможность масштабировать на новые рынки без изобретения велосипеда.',
        risk: 'При смене людей всё начинается с нуля.'
      },
      { 
        id: 'FR-020', 
        desc: 'Архитектура для автоматизации', 
        priority: 'must',
        why: 'Пилот — фундамент для автоматизации. Нужно сразу проектировать с учётом масштабирования.',
        impact: 'Переход к автоматизации без переделки всего с нуля.',
        risk: 'Ручной процесс, который невозможно автоматизировать.'
      },
    ],
  }

  const risks = [
    { 
      title: 'Блокировка парсинга', 
      desc: 'Сайты конкурентов могут блокировать автоматический сбор данных или использовать CAPTCHA.',
      mitigation: 'Используем ротацию IP, человеческие паттерны запросов, резервные методы сбора. Часть данных собираем вручную.',
      probability: 'Средняя',
      impact: 'Высокий'
    },
    { 
      title: 'Изменение структуры сайтов', 
      desc: 'Конкуренты могут изменить структуру страниц, что сломает парсеры.',
      mitigation: 'Модульная архитектура парсеров. Мониторинг работоспособности. Быстрое исправление (SLA 48 часов).',
      probability: 'Высокая',
      impact: 'Средний'
    },
    { 
      title: 'Неполнота данных из открытых источников', 
      desc: 'Важная информация может быть недоступна публично (внутренние тарифы, A/B тесты).',
      mitigation: 'Комбинируем источники: официальные + отзывы + чаты. Указываем степень уверенности в данных.',
      probability: 'Высокая',
      impact: 'Средний'
    },
    { 
      title: 'Языковые барьеры', 
      desc: 'Локальные источники на испанском (Латам), португальском, арабском требуют перевода.',
      mitigation: 'Используем LLM для перевода и анализа. Привлекаем локальных аналитиков для валидации.',
      probability: 'Средняя',
      impact: 'Средний'
    },
    { 
      title: 'Задержка в получении данных', 
      desc: 'Некоторые изменения публикуются с задержкой или не публикуются вовсе.',
      mitigation: 'Множественные источники. Кросс-валидация. Мониторинг чатов водителей как раннее предупреждение.',
      probability: 'Средняя',
      impact: 'Средний'
    },
    { 
      title: 'Качество анализа LLM', 
      desc: 'AI может неправильно классифицировать или интерпретировать данные.',
      mitigation: 'Человеческая валидация критичных инсайтов. Итеративное улучшение промптов. Обратная связь от команды.',
      probability: 'Средняя',
      impact: 'Средний'
    },
  ]

  const competitors = [
    { name: 'InDriver', why: 'Лидер рынка в Латам. Уникальная модель — пассажир предлагает цену. Главный конкурент.', focus: 'Ценообразование, водительские условия' },
    { name: 'Didi', why: 'Прямой конкурент с китайскими ресурсами. Копирует стратегии по регионам.', focus: 'Продуктовые фичи, экспансия' },
    { name: 'Uber', why: 'Глобальный лидер. Зрелые решения, которые потом копируют все остальные.', focus: 'Инновации, best practices' },
    { name: 'Cabify', why: 'Премиальный сегмент. Другая модель ценности, фокус на качестве.', focus: 'Премиум-сегмент, дифференциация' },
  ]

  const integrations = [
    { name: 'Web scraping (сайты конкурентов)', why: 'Основной источник продуктовой информации и тарифов.' },
    { name: 'App Store / Google Play API', why: 'Релиз-ноты и рейтинги — индикатор продуктовых изменений.' },
    { name: 'Сбор отзывов (Trustpilot, локальные площадки)', why: 'Голос пользователей — понимание восприятия рынка.' },
    { name: 'Telegram API (публичные чаты)', why: 'Инсайдерская информация от водителей.' },
    { name: 'OpenAI / Claude API', why: 'Анализ, классификация и генерация инсайтов.' },
    { name: 'Notion / Confluence API', why: 'Интеграция с базой знаний команды.' }
  ]

  const getPriorityBadge = (priority) => {
    const styles = {
      must: 'bg-red-50 text-red-700 border-red-200',
      should: 'bg-amber-50 text-amber-700 border-amber-200',
      nice: 'bg-slate-50 text-slate-600 border-slate-200'
    }
    const labels = { must: 'Must Have', should: 'Should Have', nice: 'Nice to Have' }
    return <span className={`px-2 py-0.5 text-xs rounded border ${styles[priority]}`}>{labels[priority]}</span>
  }

  const tabLabels = {
    parsing: 'Сбор данных',
    analysis: 'Анализ', 
    output: 'Результаты',
    infra: 'Инфраструктура'
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">Yango Competitive Intelligence</h1>
            <p className="text-xs text-slate-500">Мониторинг конкурентов — PRD + Декомпозиция v1.0</p>
          </div>
          <span className="text-xs px-2 py-1 border border-slate-200 rounded text-slate-500">Пилот: Перу</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-5">
        
        {/* 1. Executive Summary */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-2 flex items-center gap-2">1. Executive Summary</h2>
          <p className="text-sm text-slate-600 leading-relaxed mb-4">
            Yango работает на высококонкурентных рынках (Латам, Африка, СНГ, Пакистан), где InDriver, Didi, Uber и локальные игроки постоянно меняют тактику. Цель проекта — создать систему автоматизированного мониторинга, которая превращает данные о конкурентах в гипотезы для продуктовой команды и решения для бизнеса.
          </p>
          
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-3">
            <h4 className="text-xs font-medium text-blue-800 mb-1">Зачем это нужно</h4>
            <p className="text-xs text-blue-700">
              Конкуренты двигаются быстро: InDriver меняет модель ценообразования, Didi запускает промо, Uber тестирует новые фичи. 
              Кто видит эти изменения первым — тот реагирует первым. Система даёт информационное преимущество, которое превращается в рыночное.
            </p>
          </div>
        </div>

        {/* 2. Problem Statement */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">2. Описание проблемы</h2>
          
          <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">2.1 Текущие болевые точки</h3>
          <div className="space-y-3 mb-4">
            {[
              { problem: 'Изменения конкурентов замечаем с задержкой', why: 'Узнаём от пользователей или из СМИ, когда уже поздно реагировать' },
              { problem: 'Нет системного понимания тарифной политики конкурентов', why: 'Принимаем решения по ценам без данных о рынке' },
              { problem: 'Продуктовые решения конкурентов остаются незамеченными', why: 'Фичи, которые работают у других, могли бы работать у нас' },
              { problem: 'Ручной мониторинг не масштабируется', why: 'Один аналитик не может следить за 4+ конкурентами в 10+ странах' },
              { problem: 'Данные не структурированы и теряются', why: 'Каждый раз собираем информацию с нуля, нет исторического контекста' },
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-3 p-2 bg-slate-50 rounded-lg">
                <span className="text-amber-500 mt-0.5 text-lg">•</span>
                <div>
                  <p className="text-sm text-slate-700">{item.problem}</p>
                  <p className="text-xs text-slate-500 mt-0.5">→ {item.why}</p>
                </div>
              </div>
            ))}
          </div>

          <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">2.2 Желаемый результат</h3>
          <p className="text-sm text-slate-600 mb-3">
            Команда Yango видит изменения на конкурентных рынках в реальном времени, понимает логику и мотивацию конкурентов, принимает решения быстрее и увереннее на основе данных.
          </p>
          
          <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-3">
            <h4 className="text-xs font-medium text-emerald-800 mb-1">Ключевой результат</h4>
            <p className="text-xs text-emerald-700">
              Продуктовая команда получает еженедельный дайджест с изменениями конкурентов, структурированными по категориям, 
              с гипотезами для действий. Не сырые данные, а готовые инсайты для принятия решений.
            </p>
          </div>
        </div>

        {/* 3. Goals */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">3. Цели проекта</h2>
          <div className="space-y-3">
            {[
              { goal: 'Сократить время обнаружения изменений конкурентов до 24-48 часов', why: 'Скорость реакции = конкурентное преимущество', metric: 'Time-to-insight < 48ч' },
              { goal: 'Обеспечить полноту покрытия: продукты, тарифы, промо, отзывы', why: 'Частичная картина хуже, чем отсутствие картины — даёт ложную уверенность', metric: '4 категории данных' },
              { goal: 'Превращать данные в гипотезы для продуктовой команды', why: 'Данные без интерпретации не ведут к действиям', metric: '3-5 гипотез в неделю' },
              { goal: 'Создать воспроизводимый процесс для масштабирования', why: 'Пилот на Перу должен работать для СНГ, Африки, Пакистана', metric: 'PRD + архитектура' },
              { goal: 'Подготовить фундамент для автоматизации', why: 'Ручной процесс — временное решение. Автоматизация — цель', metric: 'Roadmap автоматизации' },
            ].map((item, i) => (
              <div key={i} className="p-3 border border-slate-200 rounded-lg">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-2">
                    <span className="text-emerald-500 font-bold">{i + 1}.</span>
                    <div>
                      <p className="text-sm font-medium text-slate-700">{item.goal}</p>
                      <p className="text-xs text-slate-500 mt-1">{item.why}</p>
                    </div>
                  </div>
                  <span className="text-xs px-2 py-1 bg-emerald-50 text-emerald-700 rounded shrink-0">{item.metric}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 4. Scope */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">4. Скоуп проекта</h2>
          
          <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-3">4.1 География</h3>
          
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 mb-4">
            <h4 className="text-xs font-medium text-blue-800 mb-1">Почему Перу для пилота</h4>
            <p className="text-xs text-blue-700">
              Активная конкуренция с InDriver — показательный кейс. Данные на испанском доступны. 
              Рынок достаточно большой для значимых выводов, но не слишком сложный для пилота.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-5">
            <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200">
              <span className="text-xs font-medium px-1.5 py-0.5 bg-emerald-500 text-white rounded mb-2 inline-block">Пилот</span>
              <p className="font-medium text-sm">Перу</p>
              <p className="text-xs text-slate-500 mt-0.5">4 конкурента, испанский</p>
              <p className="text-xs text-emerald-600 mt-2">→ 4 недели</p>
            </div>
            <div className="p-3 rounded-lg bg-amber-50 border border-amber-200">
              <span className="text-xs font-medium px-1.5 py-0.5 bg-amber-500 text-white rounded mb-2 inline-block">Фаза 2</span>
              <p className="font-medium text-sm">СНГ, Африка</p>
              <p className="text-xs text-slate-500 mt-0.5">Русский, английский</p>
              <p className="text-xs text-amber-600 mt-2">→ После успешного пилота</p>
            </div>
            <div className="p-3 rounded-lg bg-slate-100 border border-slate-200">
              <span className="text-xs font-medium px-1.5 py-0.5 bg-slate-500 text-white rounded mb-2 inline-block">Фаза 3</span>
              <p className="font-medium text-sm">Латам, Пакистан</p>
              <p className="text-xs text-slate-500 mt-0.5">Локальные языки</p>
              <p className="text-xs text-slate-500 mt-2">→ Масштабирование</p>
            </div>
          </div>

          <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">4.2 Конкуренты пилота</h3>
          <div className="grid md:grid-cols-2 gap-3">
            {competitors.map((comp, i) => (
              <div key={i} className="p-3 bg-slate-50 rounded-lg">
                <h4 className="text-sm font-medium mb-1">{comp.name}</h4>
                <p className="text-xs text-slate-600 mb-2">{comp.why}</p>
                <p className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded inline-block">
                  Фокус: {comp.focus}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* 5. What We Monitor */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">5. Что мониторим</h2>
          
          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div className="p-3 bg-slate-50 rounded-lg">
              <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                1. Продукты и фичи
              </h4>
              <div className="text-xs text-slate-600 space-y-1">
                <div>• Запуск новых функций</div>
                <div>• Обновления приложений</div>
                <div>• Изменения UX/UI</div>
                <div>• A/B тесты (если видны)</div>
              </div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                2. Тарифы и цены
              </h4>
              <div className="text-xs text-slate-600 space-y-1">
                <div>• Комиссии для водителей</div>
                <div>• Цены для пассажиров</div>
                <div>• Surge pricing логика</div>
                <div>• Промо и скидки</div>
              </div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                3. Отзывы пользователей
              </h4>
              <div className="text-xs text-slate-600 space-y-1">
                <div>• Что хвалят водители</div>
                <div>• Что критикуют пассажиры</div>
                <div>• Сравнение с Yango</div>
                <div>• Причины переключения</div>
              </div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                4. Партнёрства
              </h4>
              <div className="text-xs text-slate-600 space-y-1">
                <div>• Коллаборации с брендами</div>
                <div>• Интеграции с сервисами</div>
                <div>• Корпоративные клиенты</div>
                <div>• Инвестиции и M&A</div>
              </div>
            </div>
          </div>

          <div className="bg-amber-50 border border-amber-100 rounded-lg p-3">
            <h4 className="text-xs font-medium text-amber-800 mb-1">Что НЕ включено в пилот</h4>
            <p className="text-xs text-amber-700">
              Глубокий анализ маркетинговых кампаний, работа с платными источниками данных, закрытые чаты — 
              эти зоны закладываются в следующую фазу, если пилот успешен.
            </p>
          </div>
        </div>

        {/* 6. Requirements */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">6. Функциональные требования</h2>
          
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 mb-4">
            <h4 className="text-xs font-medium text-blue-800 mb-1">Как читать приоритеты</h4>
            <p className="text-xs text-blue-700">
              <strong>Must Have</strong> — без этого пилот не имеет смысла. <strong>Should Have</strong> — сильно улучшает ценность. 
              <strong>Nice to Have</strong> — бонус для следующих этапов.
            </p>
          </div>
          
          {/* Tabs */}
          <div className="flex gap-1 mb-4 bg-slate-100 p-1 rounded-lg">
            {Object.keys(requirements).map((key) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`flex-1 text-xs py-2 px-2 rounded-md transition-all ${
                  activeTab === key 
                    ? 'bg-white shadow-sm font-medium' 
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {tabLabels[key]}
              </button>
            ))}
          </div>

          {/* Requirements list */}
          <div className="space-y-2">
            {requirements[activeTab].map((req, i) => (
              <div key={req.id} className="border border-slate-200 rounded-lg overflow-hidden">
                <button 
                  onClick={() => setOpenFR(openFR === req.id ? null : req.id)}
                  className="w-full text-left px-3 py-2 flex items-center justify-between hover:bg-slate-50"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-slate-400">{req.id}</span>
                    <span className="text-sm">{req.desc}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {getPriorityBadge(req.priority)}
                    <span className="text-slate-400">{openFR === req.id ? '−' : '+'}</span>
                  </div>
                </button>
                {openFR === req.id && (
                  <div className="px-3 py-3 bg-slate-50 border-t border-slate-200 space-y-2">
                    <div>
                      <p className="text-xs font-medium text-slate-700">Зачем это нужно</p>
                      <p className="text-xs text-slate-600">{req.why}</p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-700">На что влияет</p>
                      <p className="text-xs text-slate-600">{req.impact}</p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-700">Риск без реализации</p>
                      <p className="text-xs text-slate-600">{req.risk}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 7. User Flow */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">7. Пользовательский сценарий (User Flow)</h2>
          
          <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-4">
            {['Сбор', 'Обработка', 'Анализ', 'Дайджест', 'Гипотезы', 'Решения'].map((step, idx) => (
              <div key={idx} className="flex items-center gap-2 shrink-0">
                <div className="flex items-center justify-center w-7 h-7 rounded-full bg-slate-900 text-white text-xs font-medium">
                  {idx + 1}
                </div>
                <span className="text-xs text-slate-600">{step}</span>
                {idx < 5 && <div className="w-6 h-px bg-slate-300" />}
              </div>
            ))}
          </div>

          <div className="space-y-3">
            {[
              { step: 'Система собирает данные из открытых источников', why: 'Парсинг сайтов, отзывов, релиз-ноутов — автоматически или по расписанию', who: 'Система' },
              { step: 'Данные структурируются и валидируются', why: 'Фильтрация шума, классификация по категориям, привязка к конкуренту', who: 'Система + валидация' },
              { step: 'AI анализирует изменения и выделяет важное', why: 'Не всё важно одинаково. AI приоритизирует по влиянию на бизнес', who: 'AI + аналитик' },
              { step: 'Формируется еженедельный дайджест', why: 'Структурированный формат: что изменилось, у кого, почему это важно', who: 'Система' },
              { step: 'Аналитик формулирует гипотезы', why: 'Данные → интерпретация → actionable insights для продукта', who: 'Аналитик' },
              { step: 'Продуктовая команда принимает решения', why: 'Гипотезы обсуждаются, приоритизируются, попадают в roadmap', who: 'Продукт' },
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-3 p-2 bg-slate-50 rounded-lg">
                <span className="font-medium text-slate-400 text-sm">{i + 1}.</span>
                <div className="flex-1">
                  <p className="text-sm text-slate-700">{item.step}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{item.why}</p>
                </div>
                <span className="text-xs px-2 py-1 bg-white border border-slate-200 rounded text-slate-500 shrink-0">{item.who}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 8. Phases */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">8. Этапы реализации</h2>
          
          <div className="flex gap-2 mb-4">
            {phases.map((phase, idx) => (
              <button
                key={idx}
                onClick={() => setActivePhase(idx)}
                className={`flex-1 p-2 rounded-lg border text-left transition-all ${
                  activePhase === idx 
                    ? 'border-slate-900 bg-slate-900 text-white' 
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}
              >
                <div className="text-[10px] opacity-60">Этап {idx + 1}</div>
                <div className="font-medium text-xs">{phase.name}</div>
              </button>
            ))}
          </div>

          <div className="p-4 bg-slate-50 rounded-lg space-y-3">
            <h4 className="font-medium text-sm">{phases[activePhase].title}</h4>
            
            <div className="grid md:grid-cols-2 gap-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                <p className="text-xs font-medium text-blue-800 mb-1">Зачем этот этап</p>
                <p className="text-xs text-blue-700">{phases[activePhase].why}</p>
              </div>
              <div className="p-2 bg-emerald-50 rounded-lg">
                <p className="text-xs font-medium text-emerald-800 mb-1">Что получаем</p>
                <p className="text-xs text-emerald-700">{phases[activePhase].impact}</p>
              </div>
            </div>

            <div>
              <p className="text-xs font-medium text-slate-500 mb-2">Что делаем:</p>
              <ul className="text-sm text-slate-600 space-y-1">
                {phases[activePhase].items.map((item, i) => (
                  <li key={i}>• {item}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* 9. Pilot Deliverables */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">9. Результаты пилота</h2>
          
          <div className="space-y-4">
            <div className="p-3 border border-slate-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                1.
                <h4 className="font-medium text-sm">1. Собранные данные</h4>
              </div>
              <div className="text-xs text-slate-600 space-y-1 ml-7">
                <div>• Структурированные по категориям и конкурентам</div>
                <div>• Отфильтрованные от шума</div>
                <div>• С указанием источников и степени достоверности</div>
              </div>
            </div>

            <div className="p-3 border border-slate-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                2.
                <h4 className="font-medium text-sm">2. Аналитический отчёт</h4>
              </div>
              <div className="text-xs text-slate-600 space-y-1 ml-7">
                <div>• Сравнение продуктов конкурентов</div>
                <div>• Анализ тарифной политики и динамики</div>
                <div>• Сегментация отзывов по темам и ролям</div>
                <div>• Выводы и гипотезы для продуктовой команды</div>
              </div>
            </div>

            <div className="p-3 border border-slate-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                3.
                <h4 className="font-medium text-sm">3. PRD-документ</h4>
              </div>
              <div className="text-xs text-slate-600 space-y-1 ml-7">
                <div>• Как собирали данные: шаги, источники, структура</div>
                <div>• Что можно переиспользовать для других рынков</div>
                <div>• Инструкции для воспроизведения без автоматизации</div>
                <div>• Архитектура для автоматизации (следующий этап)</div>
              </div>
            </div>
          </div>

          <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-3 mt-4">
            <h4 className="text-xs font-medium text-emerald-800 mb-1">Главное</h4>
            <p className="text-xs text-emerald-700">
              Не только "что мы узнали", но и "как это работает и масштабируется". 
              Пилот — это валидация подхода и фундамент для продуктовой фазы.
            </p>
          </div>
        </div>

        {/* 10. Risks */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">10. Риски и ограничения</h2>
          
          <div className="bg-amber-50 border border-amber-100 rounded-lg p-3 mb-4">
            <h4 className="text-xs font-medium text-amber-800 mb-1">Честный разговор о рисках</h4>
            <p className="text-xs text-amber-700">
              Мониторинг конкурентов — не волшебство. Есть ограничения: не всё доступно публично, 
              сайты меняются, данные могут быть неполными. Мы знаем эти риски и умеем с ними работать.
            </p>
          </div>
          
          <div className="space-y-2">
            {risks.map((risk, i) => (
              <div key={i} className="border border-slate-200 rounded-lg overflow-hidden">
                <button 
                  onClick={() => setOpenRisk(openRisk === i ? null : i)}
                  className="w-full text-left px-3 py-2 flex items-center justify-between hover:bg-slate-50"
                >
                  <span className="text-sm"><span className="font-medium text-slate-700">{i + 1}.</span> {risk.title}</span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      risk.probability === 'Высокая' ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-600'
                    }`}>{risk.probability}</span>
                    <span className="text-slate-400">{openRisk === i ? '−' : '+'}</span>
                  </div>
                </button>
                {openRisk === i && (
                  <div className="px-3 py-3 bg-slate-50 border-t border-slate-200 space-y-2">
                    <div>
                      <p className="text-xs font-medium text-slate-700">Суть риска</p>
                      <p className="text-xs text-slate-600">{risk.desc}</p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-emerald-700">+ Как минимизируем</p>
                      <p className="text-xs text-slate-600">{risk.mitigation}</p>
                    </div>
                    <div className="flex gap-4 pt-1">
                      <span className="text-xs text-slate-500">Вероятность: <strong>{risk.probability}</strong></span>
                      <span className="text-xs text-slate-500">Влияние: <strong>{risk.impact}</strong></span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 11. Success Metrics */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">11. Метрики успеха</h2>
          
          <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-3 mb-4">
            <h4 className="text-xs font-medium text-emerald-800 mb-1">Как понять, что пилот успешен</h4>
            <p className="text-xs text-emerald-700">
              Две главные метрики: ускорение (как быстро команда получает инсайты) и ценность (насколько эти инсайты влияют на решения).
            </p>
          </div>
          
          <div className="space-y-4">
            {[
              { label: 'Time-to-insight', value: '< 48 часов после изменения у конкурента', pct: 100, why: 'Главная метрика скорости. Если узнаём через неделю — уже поздно.' },
              { label: 'Полнота покрытия', value: '4 конкурента × 4 категории данных', pct: 100, why: 'Частичная картина опаснее отсутствия — даёт ложную уверенность.' },
              { label: 'Actionable гипотезы', value: '3-5 гипотез в неделю для продуктовой команды', pct: 80, why: 'Данные без интерпретации — просто данные. Ценность в гипотезах.' },
              { label: 'Влияние на решения', value: '≥1 решение в месяц на основе данных мониторинга', pct: 60, why: 'Конечная метрика ценности. Если данные не влияют на решения — зачем они?' },
              { label: 'Воспроизводимость', value: 'PRD позволяет запустить мониторинг нового рынка за 1 неделю', pct: 70, why: 'Пилот должен масштабироваться. Если каждый рынок с нуля — не работает.' },
            ].map((m, i) => (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600">{i + 1}. {m.label}</span>
                  <span className="font-medium text-slate-800">{m.value}</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden mb-1">
                  <div className="h-full bg-emerald-500 rounded-full transition-all" style={{ width: `${m.pct}%` }} />
                </div>
                <p className="text-xs text-slate-500">{m.why}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 12. Timeline & Cost */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">12. Сроки и стоимость</h2>
          
          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div>
              <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">Таймлайн пилота</h3>
              <div className="space-y-2">
                {[
                  { phase: 'Неделя 1', task: 'Сбор первичных данных', milestone: 'Данные собраны' },
                  { phase: 'Неделя 2', task: 'Сравнительный анализ + выводы', milestone: 'Первые инсайты' },
                  { phase: 'Неделя 3', task: 'Гипотезы для продуктовой команды', milestone: 'Гипотезы готовы' },
                  { phase: 'Неделя 4', task: 'Документация + презентация', milestone: 'PRD + финальный отчёт' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3 p-2 bg-slate-50 rounded-lg">
                    <span className="text-xs font-medium text-slate-500 w-16">{item.phase}</span>
                    <div className="flex-1">
                      <p className="text-sm text-slate-700">{item.task}</p>
                    </div>
                    <span className="text-xs text-emerald-600">→ {item.milestone}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">Стоимость пилота</h3>
              <div className="p-4 bg-slate-50 rounded-lg">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">Сбор данных</span>
                    <span className="text-sm font-medium">200 000 ₽</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">R&D + архитектура</span>
                    <span className="text-sm font-medium">350 000 ₽</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">Анализ и презентация</span>
                    <span className="text-sm text-slate-500">включено</span>
                  </div>
                  <div className="border-t border-slate-200 pt-3 flex justify-between">
                    <span className="text-sm font-medium text-slate-700">Итого (с налогами)</span>
                    <span className="text-sm font-bold text-slate-900">585 106 ₽</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-3 p-3 bg-blue-50 border border-blue-100 rounded-lg">
                <p className="text-xs text-blue-700">
                  <strong>Следующий этап (автоматизация):</strong> 800K – 1.5M ₽<br/>
                  Точная оценка — после пилота и PRD.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 13. Technical Requirements */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3 flex items-center gap-2">13. Технические требования</h2>
          
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 mb-4">
            <h4 className="text-xs font-medium text-blue-800 mb-1">Для понимания</h4>
            <p className="text-xs text-blue-700">
              Техническая часть — наша ответственность. Вам важно понимать: система строится модульно, 
              чтобы легко менять источники и добавлять новые рынки.
            </p>
          </div>
          
          <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">Интеграции</h3>
          <div className="grid md:grid-cols-2 gap-2">
            {integrations.map((item, i) => (
              <div key={i} className="p-2 bg-slate-50 rounded-lg">
                <p className="text-sm font-medium text-slate-700">{item.name}</p>
                <p className="text-xs text-slate-500">→ {item.why}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 14. Out of Scope */}
        <div className="bg-slate-100 rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3">14. Вне скоупа пилота</h2>
          
          <div className="bg-white border border-slate-200 rounded-lg p-3 mb-4">
            <h4 className="text-xs font-medium text-slate-700 mb-1">Почему важно зафиксировать границы</h4>
            <p className="text-xs text-slate-600">
              Пилот — это валидация подхода, не полноценный продукт. 
              Эти вещи сознательно откладываем на следующие этапы.
            </p>
          </div>
          
          <div className="space-y-2">
            {[
              { item: 'Глубокий анализ маркетинговых кампаний', why: 'Требует отдельной методологии и доступа к рекламным данным' },
              { item: 'Работа с платными источниками', why: 'Сначала выжимаем максимум из открытых данных' },
              { item: 'Закрытые чаты водителей', why: 'Сложный доступ, этические вопросы — отдельный проект' },
              { item: 'Полная автоматизация', why: 'Пилот — ручной/полуавтоматический процесс для валидации' },
              { item: 'Дашборды и BI', why: 'Сначала структура данных, потом визуализация' },
            ].map((item, i) => (
              <div key={i} className="p-2 bg-white border border-slate-200 rounded-lg">
                <p className="text-sm font-medium text-slate-700">{item.item}</p>
                <p className="text-xs text-slate-500">→ {item.why}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Why Us */}
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <h2 className="font-semibold text-sm mb-3">15. Почему мы</h2>
          
          <div className="space-y-3">
            {[
              { point: 'Делаем мониторинг как функцию продукта, не как агентский ресёрч', why: 'Результат — система, которая масштабируется, а не одноразовый отчёт' },
              { point: 'Умеем превращать AI + данные в работающие системы', why: 'Не просто собираем данные, а делаем их actionable' },
              { point: 'Строим процессы, которые не разваливаются', why: 'Документация, архитектура, воспроизводимость — часть deliverables' },
              { point: 'Опыт: финтех, маркетплейсы, международные рынки', why: 'Понимаем контекст высококонкурентных рынков' },
            ].map((item, i) => (
              <div key={i} className="p-3 bg-slate-50 rounded-lg">
                <p className="text-sm font-medium text-slate-700">{item.point}</p>
                <p className="text-xs text-slate-500 mt-1">→ {item.why}</p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="bg-slate-900 rounded-xl p-4 text-white">
          <h2 className="font-semibold text-sm mb-2">Готовность к старту</h2>
          <div className="space-y-2 text-sm text-slate-300">
            <p>• Начинаем сразу после согласования и предоплаты 30%</p>
            <p>• Первые инсайты — через 10 дней</p>
            <p>• Итоги пилота, PRD и структура развития — в конце 4 недели</p>
          </div>
        </div>

      </main>

      <footer className="border-t border-slate-200 bg-white mt-6">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <p className="text-xs text-slate-400 text-center">
            Yango Competitive Intelligence — PRD + Декомпозиция • Версия 1.0 • Пилот: Перу
          </p>
        </div>
      </footer>
    </div>
  )
}
