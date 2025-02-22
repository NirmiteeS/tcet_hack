import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Menu, Video, Mail, Folder, Network, CalendarDays, FileText, Bot } from "lucide-react";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
import { UserButton, useUser } from "@clerk/clerk-react";
import { ModeToggle } from "./ModeToggle";

const cn = (...classes) => classes.filter(Boolean).join(" ");

const navItems = [
  { name: "Multimodal System", href: "/documents", icon: FileText , description: "Multilingual voice and text system" },
  { name: "Workflow", href: "/workflow", icon: Network, description: "Enhance workflow" },
  { name: "Video Meet", href: "/videocall", icon: Video, description: "Join Meets and Summarize meeting transcripts" },
  { name: "Chatbot", href: "/dashboard", icon: Bot, description: "Ask anything" },
  { name: "Gmail", href: "/mail", icon: Mail, description: "Analyze and process emails" },
  { name: "Google Drive", href: "/drive", icon: Folder, description: "Store and manage files" },
  // { name: "Calendar", href: "/calendar", icon: CalendarDays, description: "Schedule tasks and meet" },
  
];

export default function Sidebar() {
  const location = useLocation();
  const { user } = useUser();

  const NavLinks = ({ onClick }) => (
    <div className="h-full w-full flex flex-col">
      <nav className="space-y-3 w-full">
        {navItems.map((item) => (
          <Link
            key={item.href}
            to={item.href}
            className={cn(
              "flex flex-col p-4 bg-[#2A2B2E] rounded-lg transition-all hover:bg-[#343538]",
              location.pathname.includes(item.href) && "bg-[#343538]"
            )}
            onClick={onClick}
          >
            <div className="flex items-center gap-3">
              <item.icon className="h-6 w-6 text-green-400" />
              <div>
                <h2 className="font-semibold">{item.name}</h2>
                <p className="text-xs text-gray-400">{item.description}</p>
              </div>
            </div>
          </Link>
        ))}
      </nav>

      {/* User Profile & Mode Toggle */}
      <div className="flex justify-between items-center p-4 mt-auto border-t border-gray-700">
        <div className="flex items-center">
          <UserButton />
          {user && <span className="ml-2 text-sm text-gray-400">{user?.fullName}</span>}
        </div>
        <ModeToggle />
      </div>
    </div>
  );

  return (
    <div
  className={cn(
    "flex h-screen bg-[#1E1F22] text-white",
    location.pathname.includes("/workflow")  ? "fixed" : "relative"
  )}
>
      {/* Sidebar for large screens, hidden on small screens */}
      <aside className="hidden lg:flex w-80 p-4 flex-col border-r border-gray-700">
        {/* Search Bar */}
        <div className="mb-4">
          <h1>Intell</h1>
        </div>
        <ScrollArea className="flex-1">
          <NavLinks />
        </ScrollArea>
      </aside>

      {/* Mobile Sidebar - Toggle Button Only */}
      <Sheet>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden absolute top-4 left-4 z-50 bg-[#2A2B2E] p-2 rounded-md"
          >
            <Menu className="h-6 w-6 text-white" />
            <span className="sr-only">Toggle navigation menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-80 p-0 bg-[#1E1F22] text-white">
          <VisuallyHidden>
            <SheetTitle>Navigation Menu</SheetTitle>
          </VisuallyHidden>
          <div className="p-4">
          <h1>Intell</h1>
          </div>
          <ScrollArea className="flex-1 p-4">
            <NavLinks />
          </ScrollArea>
        </SheetContent>
      </Sheet>
    </div>
  );
}
