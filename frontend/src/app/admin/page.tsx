'use client';

import BookSection from '@/components/admin/BookSection';
import MemberSection from '@/components/admin/MemberSection';
import BorrowingSection from '@/components/admin/BorrowingSection';

export default function AdminPage() {
  return (
    <div className="admin-page">
      <h1 className="admin-title"> Admin Dashboard</h1>

      <BookSection />
      <MemberSection />
      <BorrowingSection />
    </div>
  );
}
