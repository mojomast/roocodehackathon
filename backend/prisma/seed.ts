// This is the seeding script for the NestJS backend project.
// It will populate the database with test users, add fake currency, and include sample store items.

import { PrismaClient } from '@prisma/client';
import * as bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  // Create test users
  const users = [];
  for (let i = 1; i <= 5; i++) {
    const password = await bcrypt.hash(`password${i}`, 10);
    users.push({
      username: `testuser${i}`,
      email: `testuser${i}@example.com`,
      password: password,
    });
  }

  await prisma.user.createMany({
    data: users,
    skipDuplicates: true,
  });

  console.log('Created test users.');

  // Add fake currency to users
  const createdUsers = await prisma.user.findMany();
  for (const user of createdUsers) {
    await prisma.wallet.upsert({
      where: { userId: user.id },
      update: { balance: 1000 },
      create: { userId: user.id, balance: 1000 },
    });
  }

  console.log('Added fake currency to users.');

  // Add sample store items
  const storeItems = [
    { name: 'Sword of Destiny', description: 'A legendary sword.', price: 500 },
    { name: 'Shield of Protection', description: 'A sturdy shield.', price: 300 },
    { name: 'Potion of Healing', description: 'Restores health.', price: 50 },
    { name: 'Magic Ring', description: 'Increases stats.', price: 750 },
  ];

  await prisma.storeItem.createMany({
    data: storeItems,
    skipDuplicates: true,
  });

  console.log('Added sample store items.');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });