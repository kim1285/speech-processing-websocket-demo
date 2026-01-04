class Solution:
    def sortedSquares(self, nums):
        n = len(nums)
        arr = [0] * n
        index = n - 1
        a, b = 0, (len(nums)-1)
        while a < b:
            sq_a = nums[a] ** 2
            sq_b = nums[b] ** 2
            if sq_a > sq_b:
                arr[index] = sq_a
                a += 1
            elif sq_a < sq_b:
                arr[index] = sq_b
                b -= 1
            index -= 1
        return arr

nums = [-7,-3,2,3,11]
s = Solution()
print(s.sortedSquares(nums))
