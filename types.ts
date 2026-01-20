
export enum CategoryType {
  PISTA = 'Pista',
  PRODUTOS = 'Família de Produtos'
}

export enum UserRole {
  LIDER = 'LIDER',
  GERENTE = 'GERENTE'
}

export interface User {
  id: string;
  username: string;
  password?: string; // Senha para acesso
  role: UserRole;
}

export interface Transaction {
  id: string;
  family: string;
  dirtyAmount: number;
  returnedAmount: number;
  taxRate: number;
  category: CategoryType;
  profit: number;
  bleachCount: number;
  bleachCost: number;
  machineTax: number;
  timestamp: number;
  createdBy: string;
}

export interface Settings {
  taxPista: number;
  taxProdutos: number;
  bleachPrice: number;
  machineTaxRate: number;
}
