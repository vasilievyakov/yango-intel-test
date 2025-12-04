'use client'

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { cn } from '@/lib/utils'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

interface Column<T> {
    key: keyof T | string
    label: string
    format?: (value: any, row: T) => React.ReactNode
    sortable?: boolean
    highlight?: 'min' | 'max'
}

interface ComparisonTableProps<T extends Record<string, any>> {
    data: T[]
    columns: Column<T>[]
    className?: string
}

export function ComparisonTable<T extends Record<string, any>>({
    data,
    columns,
    className,
}: ComparisonTableProps<T>) {
    const [sortKey, setSortKey] = useState<string | null>(null)
    const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

    const handleSort = (key: string) => {
        if (sortKey === key) {
            setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
        } else {
            setSortKey(key)
            setSortDir('asc')
        }
    }

    const sortedData = [...data].sort((a, b) => {
        if (!sortKey) return 0
        const aVal = a[sortKey]
        const bVal = b[sortKey]
        if (typeof aVal === 'number' && typeof bVal === 'number') {
            return sortDir === 'asc' ? aVal - bVal : bVal - aVal
        }
        return sortDir === 'asc'
            ? String(aVal).localeCompare(String(bVal))
            : String(bVal).localeCompare(String(aVal))
    })

    // Calculate min/max for highlighting
    const getMinMax = (key: string) => {
        const values = data.map(d => d[key]).filter(v => typeof v === 'number') as number[]
        return { min: Math.min(...values), max: Math.max(...values) }
    }

    return (
        <div className={cn('rounded-md border', className)}>
            <Table>
                <TableHeader>
                    <TableRow>
                        {columns.map((col) => (
                            <TableHead key={String(col.key)}>
                                {col.sortable !== false ? (
                                    <Button
                                        variant="ghost"
                                        onClick={() => handleSort(String(col.key))}
                                        className="h-8 px-2 -ml-2 font-medium"
                                    >
                                        {col.label}
                                        {sortKey === col.key ? (
                                            sortDir === 'asc' ? (
                                                <ArrowUp className="ml-2 h-4 w-4" />
                                            ) : (
                                                <ArrowDown className="ml-2 h-4 w-4" />
                                            )
                                        ) : (
                                            <ArrowUpDown className="ml-2 h-4 w-4 opacity-50" />
                                        )}
                                    </Button>
                                ) : (
                                    col.label
                                )}
                            </TableHead>
                        ))}
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {sortedData.map((row, rowIndex) => (
                        <TableRow key={rowIndex}>
                            {columns.map((col) => {
                                const value = row[col.key as string]
                                const formatted = col.format ? col.format(value, row) : value

                                let cellClass = ''
                                if (col.highlight && typeof value === 'number') {
                                    const { min, max } = getMinMax(String(col.key))
                                    if (col.highlight === 'min' && value === min) {
                                        cellClass = 'text-green-600 font-semibold'
                                    } else if (col.highlight === 'max' && value === max) {
                                        cellClass = 'text-green-600 font-semibold'
                                    } else if (col.highlight === 'min' && value === max) {
                                        cellClass = 'text-red-600'
                                    } else if (col.highlight === 'max' && value === min) {
                                        cellClass = 'text-red-600'
                                    }
                                }

                                return (
                                    <TableCell key={String(col.key)} className={cellClass}>
                                        {formatted ?? '—'}
                                    </TableCell>
                                )
                            })}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}
