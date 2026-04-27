import * as React from "react"
import { motion } from "framer-motion"
import { Link, useNavigate } from "react-router-dom"
import { ImageSlider } from "@/components/ui/image-slider"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Globe, Apple } from "lucide-react"

const images = [
  "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900&auto=format&fit=crop&q=60",
  "https://images.unsplash.com/photo-1518770660439-4636190af475?w=900&auto=format&fit=crop&q=60",
  "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=900&auto=format&fit=crop&q=60",
  "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=900&auto=format&fit=crop&q=60",
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2,
    },
  },
}

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring" as const,
      stiffness: 100,
      damping: 12,
    },
  },
}

export default function LoginPage() {
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [isRegister, setIsRegister] = React.useState(false)
  const [error, setError] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const endpoint = isRegister ? "/auth/register" : "/auth/token"
      let res: Response
      if (isRegister) {
        res = await fetch("http://localhost:8000" + endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        })
        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.detail || "Registration failed")
        }
        setIsRegister(false)
        setError("Registration successful! Please sign in.")
      } else {
        const formData = new URLSearchParams()
        formData.append("username", email)
        formData.append("password", password)
        res = await fetch("http://localhost:8000" + endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: formData,
        })
        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.detail || "Invalid credentials")
        }
        const data = await res.json()
        localStorage.setItem("token", data.access_token)
        navigate("/dashboard")
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full h-screen min-h-[700px] flex items-center justify-center bg-background p-4">
      <motion.div
        className="w-full max-w-5xl h-[700px] grid grid-cols-1 lg:grid-cols-2 rounded-2xl overflow-hidden shadow-2xl border"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        {/* Left side: Image Slider */}
        <div className="hidden lg:block">
          <ImageSlider images={images} interval={4000} />
        </div>

        {/* Right side: Login Form */}
        <div className="w-full h-full bg-card text-card-foreground flex flex-col items-center justify-center p-8 md:p-12">
          <motion.div
            className="w-full max-w-sm"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.h1 variants={itemVariants} className="text-3xl font-bold tracking-tight mb-2">
              {isRegister ? "Create Account" : "Welcome Back"}
            </motion.h1>
            <motion.p variants={itemVariants} className="text-muted-foreground mb-8">
              {isRegister
                ? "Enter your details to create a new account."
                : "Enter your credentials to access your account."}
            </motion.p>

            <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <Button variant="outline" type="button">
                <Globe className="mr-2 h-4 w-4" />
                Google
              </Button>
              <Button variant="outline" type="button">
                <Apple className="mr-2 h-4 w-4" />
                Apple
              </Button>
            </motion.div>

            <motion.div variants={itemVariants} className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </motion.div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <motion.div variants={itemVariants} className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </motion.div>
              <motion.div variants={itemVariants} className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                  {!isRegister && (
                    <a href="#" className="text-sm font-medium text-primary hover:underline">
                      Forgot password?
                    </a>
                  )}
                </div>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </motion.div>
              {error && (
                <motion.div variants={itemVariants} className={`text-sm ${error.includes("successful") ? "text-green-600" : "text-red-500"}`}>
                  {error}
                </motion.div>
              )}
              <motion.div variants={itemVariants}>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? "Please wait..." : isRegister ? "Sign Up" : "Log In"}
                </Button>
              </motion.div>
            </form>

            <motion.p variants={itemVariants} className="text-center text-sm text-muted-foreground mt-8">
              {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
              <button
                type="button"
                onClick={() => {
                  setIsRegister(!isRegister)
                  setError("")
                }}
                className="font-medium text-primary hover:underline"
              >
                {isRegister ? "Sign in" : "Sign up"}
              </button>
            </motion.p>

            <motion.div variants={itemVariants} className="text-center mt-4">
              <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">
                ← Back to home
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}
