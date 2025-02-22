import { SignUp, useUser } from "@clerk/clerk-react";

const SignUpPage = () => {
  const { user } = useUser();

  return (
    <div className="flex justify-center items-center h-screen">
        <SignUp forceRedirectUrl="/documents" />
    </div>
  )
}

export default SignUpPage